from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Submission
from problems.models import Problem
import subprocess
import tempfile
import os

@login_required
def submit_code(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)

    if request.method == "POST":
        code = request.POST.get("code")
        language = request.POST.get("language")
        submission = Submission.objects.create(
            user=request.user,
            problem=problem,
            code=code,
            language=language,
        )

        # Judge the submission
        verdict, output, error = judge_submission(code, language, problem.test_cases)

        # Save results to submission
        submission.result = verdict
        submission.output = output
        submission.error = error
        submission.save()

        # Update member stats
        member = submission.user.member
        member.total_submissions += 1

        already_solved = Submission.objects.filter(
            user=submission.user,
            problem=submission.problem,
            result="Accepted"
        ).exclude(id=submission.id).exists()

        if submission.result == "Accepted" and not already_solved:
            member.problems_solved += 1

        member.save()

        return redirect('submissions:submission_detail', submission_id=submission.id)



    return render(request, "submissions/submit.html", {"problem": problem})


@login_required
def submission_detail(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    return render(request, "submissions/submission_detail.html", {"submission": submission})


def judge_submission(code, language, test_cases):
    with tempfile.TemporaryDirectory() as tmpdirname:
        filename = ""
        run_cmd = []

        try:
            # Write code to file based on language
            if language == "python":
                filename = os.path.join(tmpdirname, "main.py")
                with open(filename, "w") as f:
                    f.write(code)
                run_cmd = ["python", filename]

            elif language == "c":
                source_file = os.path.join(tmpdirname, "main.c")
                exec_file = os.path.join(tmpdirname, "main.exe" if os.name == 'nt' else "main")
                with open(source_file, "w") as f:
                    f.write(code)
                compile = subprocess.run(["gcc", source_file, "-o", exec_file], capture_output=True)
                if compile.returncode != 0:
                    return "Compilation Error", "", compile.stderr.decode()
                run_cmd = [exec_file]

            elif language == "cpp":
                source_file = os.path.join(tmpdirname, "main.cpp")
                exec_file = os.path.join(tmpdirname, "main.exe" if os.name == 'nt' else "main")
                with open(source_file, "w") as f:
                    f.write(code)
                compile = subprocess.run(["g++", source_file, "-o", exec_file], capture_output=True)
                if compile.returncode != 0:
                    return "Compilation Error", "", compile.stderr.decode()
                run_cmd = [exec_file]

            elif language == "java":
                source_file = os.path.join(tmpdirname, "Main.java")
                with open(source_file, "w") as f:
                    f.write(code)
                compile = subprocess.run(["javac", source_file], capture_output=True)
                if compile.returncode != 0:
                    return "Compilation Error", "", compile.stderr.decode()
                run_cmd = ["java", "-cp", tmpdirname, "Main"]

            # Loop through test cases
            for i, case in enumerate(test_cases):
                input_data = case["input"]
                expected_output = case["output"]

                input_file = os.path.join(tmpdirname, "input.txt")
                with open(input_file, "w") as f:
                    f.write(input_data)

                result = subprocess.run(
                    run_cmd,
                    stdin=open(input_file),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5,
                )

                output = result.stdout.decode().strip()
                error = result.stderr.decode().strip()

                if error:
                    return f"Runtime Error on test case {i+1}", output, error

                if output != expected_output.strip():
                    return f"Wrong Answer on test case {i+1}", output, ""

            return "Accepted", output, ""

        except subprocess.TimeoutExpired:
            return "Time Limit Exceeded", "", ""

        except Exception as e:
            return "Error", "", str(e)
