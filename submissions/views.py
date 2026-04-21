# submissions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.conf import settings

from .models import Submission, SubmissionResult, AIHintUsage
from problems.models import Problem, TestCase

import subprocess
import tempfile
import os
import re
import time
import google.generativeai as genai

from django.utils import timezone
from datetime import timedelta


# Configure the Gemini AI client
genai.configure(api_key=settings.GEMINI_API_KEY)

# -------------------------------
# Submissions List View (NEW)
# -------------------------------
@login_required
def submission_list(request):
    """Display all submissions by the current user."""
    submissions = Submission.objects.filter(user=request.user)\
        .select_related('problem')\
        .order_by('-submitted_at')
    
    # Add pagination (20 submissions per page)
    paginator = Paginator(submissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'submissions/submission_list.html', {
        'page_obj': page_obj,
        'submissions': page_obj,
    })


# -------------------------------
# Custom run (no DB persistence)
# -------------------------------
@login_required
@require_POST
def run_custom(request, problem_id):
    try:
        code = request.POST.get("code", "")
        language = request.POST.get("language", "python")
        custom_input = request.POST.get("custom_input", "")

        if not code.strip():
            return JsonResponse({"error": "No code provided"}, status=400)

        output, exec_time = execute_code(language, code, custom_input)
        
        # Check for specific error messages
        if output.startswith("Compilation Error") or \
           output.startswith("Runtime Error") or \
           output.startswith("⏳"):
            return JsonResponse({"error": output, "execution_time": exec_time})
            
        return JsonResponse({"output": output, "execution_time": exec_time})

    except Exception as e:
        return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)


_DOCKER_IMAGES = {
    "python": "python:3.11-slim",
    "cpp":    "gcc:12",
    "c":      "gcc:12",
    "java":   "eclipse-temurin:17-jdk-jammy",
}


def _to_docker_path(host_path):
    """Convert a host path to a Docker-mountable path (handles Windows drives)."""
    p = host_path.replace("\\", "/")
    if len(p) >= 2 and p[1] == ":":
        p = "/" + p[0].lower() + p[2:]
    return p


def execute_code(language, code, user_input=""):
    """Run code inside an isolated Docker container with resource limits."""
    if language not in _DOCKER_IMAGES:
        return "Unsupported language", 0.0

    image = _DOCKER_IMAGES[language]

    with tempfile.TemporaryDirectory() as tmpdir:
        if language == "python":
            with open(os.path.join(tmpdir, "main.py"), "w", encoding="utf-8") as f:
                f.write(code)
            run_script = "python /sandbox/main.py"

        elif language == "cpp":
            with open(os.path.join(tmpdir, "main.cpp"), "w", encoding="utf-8") as f:
                f.write(code)
            run_script = (
                "g++ /sandbox/main.cpp -O2 -std=c++17 -o /tmp/main 2>/tmp/cerr"
                " || { echo 'Compilation Error:'; cat /tmp/cerr; exit 1; };"
                " /tmp/main"
            )

        elif language == "c":
            with open(os.path.join(tmpdir, "main.c"), "w", encoding="utf-8") as f:
                f.write(code)
            run_script = (
                "gcc /sandbox/main.c -O2 -std=c11 -o /tmp/main 2>/tmp/cerr"
                " || { echo 'Compilation Error:'; cat /tmp/cerr; exit 1; };"
                " /tmp/main"
            )

        elif language == "java":
            match = re.search(r"public\s+class\s+(\w+)", code)
            class_name = match.group(1) if match else "Main"
            with open(os.path.join(tmpdir, f"{class_name}.java"), "w", encoding="utf-8") as f:
                f.write(code)
            run_script = (
                f"javac /sandbox/{class_name}.java -d /tmp 2>/tmp/cerr"
                f" || {{ echo 'Compilation Error:'; cat /tmp/cerr; exit 1; }};"
                f" java -cp /tmp {class_name}"
            )

        sandbox_path = _to_docker_path(tmpdir)

        docker_cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "256m",
            "--memory-swap", "256m",
            "--cpus", "0.5",
            "--pids-limit", "50",
            "-v", f"{sandbox_path}:/sandbox:ro",
            image,
            "sh", "-c", run_script,
        ]

        try:
            start_time = time.time()
            result = subprocess.run(
                docker_cmd,
                input=user_input.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=15,  # 5 s execution + buffer for Docker startup
            )
            execution_time = round((time.time() - start_time) * 1000, 2)

            output = result.stdout.decode(errors="replace")
            err = result.stderr.decode(errors="replace")

            if output.startswith("Compilation Error"):
                return output, execution_time
            if result.returncode != 0:
                return f"Runtime Error: {err or output}", execution_time
            if err:
                return err, execution_time
            return output, execution_time

        except subprocess.TimeoutExpired:
            return "⏳ Time Limit Exceeded", 5000.0
        except FileNotFoundError:
            return "Runtime Error: Docker is not installed or not in PATH", 0.0
        except Exception as e:
            return f"Runtime Error: {str(e)}", 0.0


def judge_submission(code, language, test_cases):
    """Run user code against all test cases."""
    case_results = []
    all_passed = True
    any_runtime = False
    total_time = 0.0

    for tc in test_cases:
        inp = tc.input_data
        expected = tc.output_data

        output, exec_time = execute_code(language, code, inp)
        total_time += exec_time
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
            "execution_time": exec_time,
        })

    verdict = "Accepted" if all_passed else ("Runtime Error" if any_runtime else "Wrong Answer")
    return verdict, case_results, total_time


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
        verdict, case_results, total_time = judge_submission(code, language, test_cases)

        return render(
            request,
            "submissions/run_results.html",
            {
                "problem": problem,
                "language": language,
                "verdict": verdict,
                "code": code,
                "execution_time": round(total_time, 2),
                "results": [
                    {
                        "test_case": r["test_case"],
                        "user_output": r["output"],
                        "passed": (r["status"] == "Passed"),
                        "execution_time": r["execution_time"],
                    }
                    for r in case_results
                ],
            },
        )

    # SUBMIT (persist)
    test_cases = problem.test_cases.all().order_by("id")
    verdict, case_results, total_time = judge_submission(code, language, test_cases)

    # Collect first error output if any runtime/compile errors occurred
    first_error = next(
        (r["output"] for r in case_results
         if r["status"] in ("Runtime Error", "Time Limit Exceeded", "Compilation Error")),
        "",
    )

    submission = Submission.objects.create(
        user=request.user,
        problem=problem,
        language=language,
        code=code,
        result=verdict,
        is_correct=(verdict == "Accepted"),
        error=first_error or "",
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

    # ✅ FIX: use kwargs for redirect
    return redirect("submissions:submission_detail", submission_id=submission.id)


@login_required
def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id, user=request.user)
    results = submission.results.select_related("test_case").all()
    return render(
        request,
        "submissions/submission_detail.html",
        {"submission": submission, "results": results},
    )


# -------------------------------
# AI Hint with usage limits
# -------------------------------

# Primary: fast and cheap. Fallback: more capable.
_AI_MODELS = ["gemini-2.5-flash-lite", "gemini-2.5-flash"]

PROMPTS = {
    "hint": (
        "You are a competitive programming mentor. "
        "Read the problem and the user's code carefully, then give a SHORT (2-3 sentences), "
        "specific, actionable hint that points to the single most critical issue. "
        "Do NOT give the full solution or write corrected code. "
        "Mention the actual bug or algorithmic flaw you found and suggest the next step.\n\n"
        "{context}"
    ),
    "review": (
        "You are an expert competitive programming code reviewer. "
        "Review the code below and give a concise review (5-8 bullet points) covering:\n"
        "- **Correctness**: will it produce the right output?\n"
        "- **Edge Cases**: any missed inputs?\n"
        "- **Code Quality**: naming and readability\n"
        "- **Efficiency**: any obvious optimizations?\n"
        "Do NOT provide the complete corrected solution.\n\n"
        "{context}"
    ),
    "complexity": (
        "You are an algorithm complexity analyst. "
        "Analyze the code and respond with exactly these four sections using markdown:\n"
        "- **Time Complexity**: big-O with a one-line explanation\n"
        "- **Space Complexity**: big-O with a one-line explanation\n"
        "- **Bottleneck**: the single most expensive operation\n"
        "- **Optimization**: one specific improvement (no full solution)\n\n"
        "{context}"
    ),
}


def _build_context(problem, language, code):
    return (
        f"**Problem:** {problem.title}\n"
        f"**Description:** {problem.description}\n"
        f"**Input format:** {problem.input_format}\n"
        f"**Output format:** {problem.output_format}\n"
        f"**Constraints:** {problem.constraints}\n\n"
        f"**User's {language} code:**\n```{language}\n{code}\n```"
    )


def _call_gemini(prompt):
    last_exc = None
    for model_name in _AI_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = response.text.strip() if hasattr(response, "text") else ""
            if text:
                return text, model_name
        except Exception as e:
            print(f"AI [{model_name}] {type(e).__name__}: {e}")
            last_exc = e
    raise last_exc


def _friendly_error(exc):
    name = type(exc).__name__
    msg = str(exc)
    if name == "ResourceExhausted" or "429" in msg or "quota" in msg.lower():
        return "AI quota exhausted. Please try again later or contact the admin."
    if name in ("PermissionDenied", "Unauthenticated") or "403" in msg:
        return "Invalid API key. Please contact the admin."
    if name == "NotFound" or "404" in msg:
        return "AI model unavailable. Please contact the admin."
    if name in ("ServiceUnavailable", "DeadlineExceeded") or "503" in msg:
        return "AI service is temporarily down. Please try again in a moment."
    if name == "InvalidArgument" or "400" in msg:
        return "Invalid request to AI service. Please contact the admin."
    return f"AI service error ({name}). Please try again later."


@login_required
@require_POST
def ai_hint(request, problem_id):
    code = request.POST.get("code", "").strip()
    language = request.POST.get("language", "python")
    hint_type = request.POST.get("hint_type", "hint")

    if not code:
        return JsonResponse({"error": "No code to analyse. Write some code first."}, status=400)

    if hint_type not in PROMPTS:
        hint_type = "hint"

    problem = get_object_or_404(Problem, id=problem_id)

    usage, _ = AIHintUsage.objects.get_or_create(user=request.user)
    if timezone.now() - usage.last_reset >= timedelta(hours=24):
        usage.used_hints = 0
        usage.last_reset = timezone.now()
        usage.save()

    if usage.used_hints >= usage.limit:
        hours_left = 24 - int((timezone.now() - usage.last_reset).total_seconds() // 3600)
        return JsonResponse(
            {"error": "Daily hint limit reached. Come back tomorrow!", "remaining_hints": 0, "reset_in_hours": hours_left},
            status=403,
        )

    context = _build_context(problem, language, code)
    prompt = PROMPTS[hint_type].format(context=context)

    try:
        hint, used_model = _call_gemini(prompt)
        print(f"AI hint served via {used_model} for user {request.user}")

        usage.used_hints += 1
        usage.save()

        remaining = max(usage.limit - usage.used_hints, 0)
        hours_left = 24 - int((timezone.now() - usage.last_reset).total_seconds() // 3600)

        return JsonResponse({
            "hint": hint,
            "hint_type": hint_type,
            "remaining_hints": remaining,
            "reset_in_hours": hours_left,
        })

    except Exception as e:
        return JsonResponse(
            {
                "error": _friendly_error(e),
                "remaining_hints": max(usage.limit - usage.used_hints, 0),
                "reset_in_hours": 24 - int((timezone.now() - usage.last_reset).total_seconds() // 3600),
            },
            status=500,
        )