# submissions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest

from .models import Submission, SubmissionResult, AIHintUsage
from problems.models import Problem, TestCase

import subprocess
import tempfile
import os
import re
from google import genai
from django.utils import timezone
from datetime import timedelta


# -------------------------------
# Custom run (no DB persistence)
# -------------------------------
def run_custom(request, problem_id):
    if request.method == "POST":
        code = request.POST.get("code", "")
        language = request.POST.get("language", "python")
        custom_input = request.POST.get("custom_input", "")

        output = execute_code(language, code, custom_input)
        return JsonResponse({"output": output})

    return JsonResponse({"error": "Invalid request"}, status=400)


def execute_code(language, code, user_input=""):
    """Run code with custom input (⚠️ not sandboxed)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        if language == "python":
            code_file = os.path.join(tmpdir, "main.py")
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code)
            cmd = ["python", code_file]

        elif language == "cpp":
            code_file = os.path.join(tmpdir, "main.cpp")
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code)
            exe_file = os.path.join(tmpdir, "main.out")
            compile_proc = subprocess.run(
                ["g++", code_file, "-O2", "-std=c++17", "-o", exe_file],
                capture_output=True, text=True
            )
            if compile_proc.returncode != 0:
                return "Compilation Error:\n" + compile_proc.stderr
            cmd = [exe_file]

        elif language == "c":
            code_file = os.path.join(tmpdir, "main.c")
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code)
            exe_file = os.path.join(tmpdir, "main.out")
            compile_proc = subprocess.run(
                ["gcc", code_file, "-O2", "-std=c11", "-o", exe_file],
                capture_output=True, text=True
            )
            if compile_proc.returncode != 0:
                return "Compilation Error:\n" + compile_proc.stderr
            cmd = [exe_file]

        elif language == "java":
            # Detect public class name if provided
            match = re.search(r"public\s+class\s+(\w+)", code)
            class_name = match.group(1) if match else "Main"

            code_file = os.path.join(tmpdir, f"{class_name}.java")
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code)

            compile_proc = subprocess.run(
                ["javac", code_file],
                capture_output=True, text=True
            )
            if compile_proc.returncode != 0:
                return "Compilation Error:\n" + compile_proc.stderr

            cmd = ["java", "-cp", tmpdir, class_name]

        else:
            return "Unsupported language"

        try:
            result = subprocess.run(
                cmd,
                input=user_input.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
            )
            if result.stderr:
                return result.stderr.decode()
            return result.stdout.decode()
        except subprocess.TimeoutExpired:
            return "⏳ Time Limit Exceeded"
        except Exception as e:
            return f"Runtime Error: {str(e)}"


def judge_submission(code, language, test_cases):
    """Run user code against all test cases."""
    case_results = []
    all_passed = True
    any_runtime = False

    for tc in test_cases:
        inp = tc.input_data
        expected = tc.output_data

        output = execute_code(language, code, inp)
        out_stripped = (output or "").strip()

        status = "Passed"
        if out_stripped.startswith("Runtime Error"):
            status = "Runtime Error"
            any_runtime = True
            all_passed = False
        elif out_stripped.startswith("⏳"):
            status = "Time Limit Exceeded"
            any_runtime = True
            all_passed = False
        else:
            if out_stripped != expected.strip():
                status = "Failed"
                all_passed = False

        case_results.append({
            "test_case": tc,
            "output": output,
            "status": status,
        })

    verdict = "Accepted" if all_passed else ("Runtime Error" if any_runtime else "Wrong Answer")
    return verdict, case_results, None


# -------------------------------
# Submit & Detail
# -------------------------------
@login_required
def submit_code(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)

    if request.method != "POST":
        # change to your named URL if different
        return redirect("problems:problem_detail", pk=problem.id)

    language = request.POST.get("language")
    code = request.POST.get("code", "")
    action = request.POST.get("action")  # "run" or "submit"

    if action == "run":
        test_cases = problem.test_cases.filter(is_sample=True).order_by("id")
        verdict, case_results, _ = judge_submission(code, language, test_cases)

        return render(
            request,
            "submissions/run_results.html",
            {
                "problem": problem,
                "language": language,
                "verdict": verdict,
                "code": code,
                "results": [
                    {
                        "test_case": r["test_case"],
                        "user_output": r["output"],
                        "passed": (r["status"] == "Passed"),
                    }
                    for r in case_results
                ],
            },
        )

    # SUBMIT (persist)
    test_cases = problem.test_cases.all().order_by("id")
    verdict, case_results, _ = judge_submission(code, language, test_cases)

    submission = Submission.objects.create(
        user=request.user,
        problem=problem,
        language=language,
        code=code,
        result=verdict,
    )

    SubmissionResult.objects.bulk_create(
        [
            SubmissionResult(
                submission=submission,
                test_case=r["test_case"],
                user_output=r["output"],
                passed=(r["status"] == "Passed"),
            )
            for r in case_results
        ]
    )

    return redirect("submissions:submission_detail", submission.id)


@login_required
def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    results = submission.results.select_related("test_case").all()
    return render(
        request,
        "submissions/submission_detail.html",
        {"submission": submission, "results": results},
    )


# -------------------------------
# AI Hint with usage limits
# -------------------------------
@login_required
@require_POST
def ai_hint(request, problem_id):
    code = request.POST.get("code", "")
    language = request.POST.get("language", "python")

    if not code:
        return HttpResponseBadRequest("Missing code.")

    problem = get_object_or_404(Problem, id=problem_id)

    # usage check (global, not per-problem)
    usage, _ = AIHintUsage.objects.get_or_create(user=request.user)
    # reset if >24 hrs
    if timezone.now() - usage.last_reset >= timedelta(hours=24):
        usage.used_hints = 0
        usage.last_reset = timezone.now()
        usage.save()

    if usage.used_hints >= usage.limit:
        hours_left = 24 - int((timezone.now() - usage.last_reset).total_seconds() // 3600)
        return JsonResponse(
            {
                "error": "Hint limit reached. Come back in 24 hours for more.",
                "remaining_hints": 0,
                "reset_in_hours": hours_left,
            },
            status=403
        )

    # gemini client
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    prompt = f"""
You are a competitive programming mentor.
Read the problem and user's code, then return a SHORT, constructive hint (not the full solution).

Problem:
Title: {problem.title}
Description: {problem.description}
Input Format: {problem.input_format}
Output Format: {problem.output_format}
Constraints: {problem.constraints}

User language: {language}
User code:
```{language}
{code}
"""

    try:
        resp = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        hint = (getattr(resp, "text", "") or "").strip() or "No hint generated."

        # increment on success
        usage.used_hints += 1
        usage.save()

        remaining = max(usage.limit - usage.used_hints, 0)
        return JsonResponse({
            "hint": hint,
            "remaining_hints": remaining,
            "reset_in_hours": 24 - int((timezone.now() - usage.last_reset).total_seconds() // 3600)
        })

    except Exception as e:
        return JsonResponse({"error": f"AI hint service failed: {str(e)}"}, status=500)

