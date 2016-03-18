# coding: utf-8

from django.shortcuts import redirect, render

from .forms import SurveyForm
from .signals import activity_completed


class ActivityType(object):

    template_name = None
    singleton = False
    repeatable = True
    complete_session_label = "Finish and Submit"
    save_session_label = "Save for Later"

    def __init__(self, activity_state, title, description, parameters, extra_context):
        self.activity_state = activity_state
        self.title = title
        self.description = description
        self.parameters = parameters
        self.extra_context = extra_context
        self.setup()

    def setup(self):
        pass

    def get_context_data(self, session_state, **kwargs):
        kwargs.update({
            "title": self.title,
            "description": self.description,
            "help_text": getattr(self, "help_text", None),
            "complete_session_label": self.complete_session_label,
            "save_session_label": self.save_session_label,
        })
        kwargs.update(self.extra_context)
        return kwargs

    def completed_sessions(self):
        # @@@ move on to model and proxy
        return self.activity_state.all_sessions.filter(completed__isnull=False).order_by("-started")


class Survey(ActivityType):

    template_name = "pinax/lms/activities/survey.html"

    def handle_get_request(self, request):
        form = SurveyForm(questions=self.questions)
        return self.render(request, form=form)

    def handle_post_request(self, request):
        form = SurveyForm(request.POST, questions=self.questions)

        if form.is_valid():
            self.session_state.data.update({"answers": form.cleaned_data})
            self.session_state.mark_completed()
            self.success_message(request)
            return redirect(self.completed_url)

        return self.render(request, form=form)


class MultiPageSurvey(Survey):

    pages = []
    template_name = "pinax/lms/activities/survey.html"

    def setup(self):
        data = self.session_state.data
        if not data:
            data = {"page": 0}
        elif not data.get("page"):
            data["page"] = 0
        self.data = data

    def get_context_data(self, **kwargs):
        context = super(MultiPageSurvey, self).get_context_data(**kwargs)
        context.update({
            "page_number": self.data["page"] + 1,
            "num_pages": len(self.pages)
        })
        return context

    def get_questions(self):
        return self.pages[self.data["page"]]

    def handle_get_request(self, request):
        if self.data["page"] == len(self.pages):
            self.already_completed_message(request)
            return redirect(self.completed_url)

        questions = self.get_questions()
        form = SurveyForm(questions=questions)
        return self.render(request, form=form)

    def handle_post_request(self, request):
        if self.data["page"] == len(self.pages):
            self.already_completed_message(request)
            return redirect(self.completed_url)

        questions = self.get_questions()
        form = SurveyForm(request.POST, questions=questions)

        if form.is_valid():
            self.session_state.data.update({"answers_%d" % self.data["page"]: form.cleaned_data})
            self.session_state.data.update({"page": self.data["page"] + 1})

            if self.data["page"] == len(self.pages):
                self.session_state.mark_completed()
                self.success_message(request)
                return redirect(self.completed_url)
            else:
                self.session_state.save()

                return redirect(self.activity_url)

        return self.render(request, form=form)


class Quiz(ActivityType):

    extra_context = {}

    def setup(self):
        if not self.session_state.data:
            self.session_state.data = {"questions": self.construct_quiz()}
            self.session_state.save()
        elif not self.session_state.data.get("questions"):
            self.session_state.data["questions"] = self.construct_quiz()
            self.session_state.save()

    def get_data(self):
        data = self.session_state.data
        if not data:
            data = {"question_number": 0}
        elif not data.get("question_number"):
            data["question_number"] = 0
        elif data["question_number"] == len(data["questions"]):
            data = None
        return data

    def get_context_data(self, **kwargs):
        context = super(Quiz, self).get_context_data(**kwargs)
        data = self.get_data()
        context.update({
            "question_number": data["question_number"] + 1,
            "num_questions": len(data["questions"]),
            "question": data["questions"][data["question_number"]]
        })
        context.update(self.extra_context)
        return context

    def handle_get_request(self, request):
        data = self.get_data()
        if data is None:
            self.already_completed_message(request)
            return redirect(self.completed_url)

    def handle_post_request(self, request):
        data = self.get_data()
        if data is None:
            self.already_completed_message(request)
            return redirect(self.completed_url)

        if request.POST.get("question_number") == str(data["question_number"] + 1):
            answer = request.POST.get("answer")
            if answer in self.valid_answer:
                self.session_state.data.update({"answer_%d" % data["question_number"]: answer})
                self.session_state.data.update({"question_number": data["question_number"] + 1})

                self.valid_response(request, data)
        return render(request)

    def valid_response(self, request, data):
        if self.is_complete(data):
            return self.completed(request)
        self.session_state.save()
        return redirect(self.activity_url)

    def is_complete(self, data):
        return data["question_number"] == len(data["questions"])

    def completed(self, request):
        self.session_state.mark_completed()
        self.success_message(request)
        activity_completed.send(sender=self, activity_key=self.activity_key, activity_session_state=self.session_state, request=request)
        return redirect(self.completed_url)


class TwoChoiceQuiz(Quiz):

    template_name = "pinax/lms/activities/two_choice_quiz.html"
    valid_answer = ["left", "right"]


class LikertQuiz(Quiz):

    template_name = "pinax/lms/activities/likert_quiz.html"
    valid_answer = ["1", "2", "3", "4", "5"]

    @property
    def extra_context(self):
        return {"scale": self.scale}


class QuizWithAnswers(Quiz):

    def previous_question_ansewr(self, data):
        previous_question = None
        previous_answer = None
        if data["question_number"] > 0:
            previous_question = data["questions"][data["question_number"] - 1]
            previous_answer = data["answer_%d" % (data["question_number"] - 1)]
            if previous_answer in ["left", "L2", "L1"]:
                previous_answer = previous_question[1][0]
            elif previous_answer in ["right", "R2", "R1"]:
                previous_answer = previous_question[1][1]
            elif previous_answer == "0":
                previous_answer = "you didn't know"
        return previous_question, previous_answer

    def get_context_data(self, **kwargs):
        context = super(QuizWithAnswers, self).get_context_data(**kwargs)
        data = self.get_data()
        previous_question, previous_answer = self.previous_question_ansewr(data)
        context.update({
            "question_number": data["question_number"] + 1,
            "num_questions": len(data["questions"]),
            "question": data["questions"][data["question_number"]],
            "previous_question": previous_question,
            "previous_answer": previous_answer,
            "question_template": self.question_template,
            "answer_template": self.answer_template,
        })
        context.update(self.extra_context)
        return context

    def handle_get_request(self, request):
        data = self.get_data()
        if data is None:
            self.already_completed_message(request)
            return redirect(self.completed_url)
        return self.render(request)

    def handle_post_request(self, request):
        data = self.get_data()
        if data is None:
            self.already_completed_message(request)
            return redirect(self.completed_url)

        if request.POST.get("question_number") == str(data["question_number"] + 1):
            answer = request.POST.get("answer")

            if answer in self.valid_answer:
                self.session_state.data.update({"answer_%d" % data["question_number"]: answer})
                self.session_state.data.update({"question_number": data["question_number"] + 1})

                return self.valid_response(request, data)
        return self.render(request)

    def completed(self, request):
        self.session_state.mark_completed()
        data = self.session_state.data
        results = []

        for i, question in enumerate(data["questions"]):
            answer = data["answer_%d" % i]
            if answer in ["left", "L2", "L1"]:
                answer = question[1][0]
            elif answer in ["right", "R2", "R1"]:
                answer = question[1][1]
            elif answer == "0":
                answer = None
            results.append((question, answer))

        ctx = {
            "title": self.title,
            "description": self.description,
            "help_text": getattr(self, "help_text", None),
            "results": results,
            "activity_key": self.activity_state.activity_key,
            "answer_template": self.answer_template,
        }
        ctx.update(self.extra_context)
        activity_completed.send(sender=self, activity_key=self.activity_key, activity_session_state=self.session_state, request=request)
        return render(request, self.completed_template_name, ctx)


class TwoChoiceWithAnswersQuiz(QuizWithAnswers):

    template_name = "pinax/lms/activities/two_choice_with_answers_quiz.html"
    completed_template_name = "pinax/lms/activities/two_choice_with_answers_quiz_completed.html"
    question_template = "pinax/lms/activities/_question.html"
    answer_template = "pinax/lms/activities/_answer.html"
    valid_answer = ["left", "right"]


class TwoChoiceLikertWithAnswersQuiz(QuizWithAnswers):

    template_name = "pinax/lms/activities/two_choice_likert_with_answers_quiz.html"
    completed_template_name = "pinax/lms/activities/two_choice_with_answers_quiz_completed.html"
    question_template = "pinax/lms/activities/_question.html"
    valid_answer = ["L2", "L1", "0", "R1", "R2"]


class ShortAnswerQuiz(Quiz):

    template_name = "pinax/lms/activities/short_answer_quiz.html"
    completed_template_name = "pinax/lms/activities/short_answer_quiz_completed.html"
    question_template = "pinax/lms/activities/_question.html"
    answer_template = "pinax/lms/activities/_question.html"

    def previous_question_answer(self, data):
        previous_question = None
        previous_answer = None
        if data["question_number"] > 0:
            previous_question = data["questions"][data["question_number"] - 1]
            previous_answer = data["answer_%d" % (data["question_number"] - 1)]
        return previous_question, previous_answer

    def get_context_data(self, **kwargs):
        context = super(ShortAnswerQuiz, self).get_context_data(**kwargs)
        data = self.get_data()
        previous_question, previous_answer = self.previous_question_ansewr(data)
        context.update({
            "question_number": data["question_number"] + 1,
            "num_questions": len(data["questions"]),
            "question": data["questions"][data["question_number"]],
            "previous_question": previous_question,
            "previous_answer": previous_answer,
            "question_template": self.question_template,
            "answer_template": self.answer_template,
        })
        context.update(self.extra_context)
        return context

    def handle_get_request(self, request):
        data = self.get_data()
        if data is None:
            self.already_completed_message(request)
            return redirect(self.completed_url)
        return self.render(request)

    def handle_post_request(self, request):
        data = self.get_data()
        if data is None:
            self.already_completed_message(request)
            return redirect(self.completed_url)

        if request.POST.get("question_number") == str(data["question_number"] + 1):
            answer = request.POST.get("answer")

            self.session_state.data.update({"answer_%d" % data["question_number"]: answer})
            self.session_state.data.update({"question_number": data["question_number"] + 1})

            return self.valid_response(request, data)
        return self.render(request)

    def completed(self, request):
        self.session_state.mark_completed()
        data = self.session_state.data
        results = []

        for i, question in enumerate(data["questions"]):
            answer = data["answer_%d" % i]
            results.append((question, answer))

        ctx = {
            "title": self.title,
            "description": self.description,
            "help_text": getattr(self, "help_text", None),
            "results": results,
            "activity_key": self.activity_state.activity_key,
            "answer_template": self.answer_template,
        }
        ctx.update(self.extra_context)
        activity_completed.send(sender=self, activity_key=self.activity_key, activity_session_state=self.session_state, request=request)
        return render(request, self.completed_template_name, ctx)


class MultipleShortAnswerQuiz(Quiz):

    template_name = "pinax/lms/activities/multiple_short_answer_quiz.html"
    completed_template_name = "pinax/lms/activities/multiple_short_answer_quiz_completed.html"
    question_template = "pinax/lms/activities/_question.html"
    answer_template = "pinax/lms/activities/_question.html"

    def get_context_data(self, **kwargs):
        context = super(MultipleShortAnswerQuiz, self).get_context_data(**kwargs)
        data = self.get_data()
        context.update({
            "question_number": data["question_number"] + 1,
            "num_questions": len(data["questions"]),
            "question": data["questions"][data["question_number"]],
            "question_template": self.question_template,
            "answer_template": self.answer_template,
        })
        context.update(self.extra_context)
        return context

    def handle_get_request(self, request):
        data = self.get_data()
        if data is None:
            self.already_completed_message(request)
            return redirect(self.completed_url)
        return self.render(request)

    def handle_post_request(self, request):
        data = self.get_data()
        if data is None:
            self.already_completed_message(request)
            return redirect(self.completed_url)

        question = data["questions"][data["question_number"]]

        if request.POST.get("question_number") == str(data["question_number"] + 1):
            answers = [None] * len(question[1])
            for key, value in request.POST.items():
                if key.startswith("answer_"):
                    answers[int(key.split("_")[1])] = value

            self.session_state.data.update({"answer_%d" % data["question_number"]: answers})
            self.session_state.data.update({"question_number": data["question_number"] + 1})

            return self.valid_response(request, data)
        return self.render(request)

    def completed(self, request):
        self.session_state.mark_completed()
        data = self.session_state.data
        results = []

        for i, question in enumerate(data["questions"]):
            answer = data["answer_%d" % i]
            results.append((question[0], zip(question[1], answer)))

        ctx = {
            "title": self.title,
            "description": self.description,
            "help_text": getattr(self, "help_text", None),
            "results": results,
            "activity_key": self.activity_state.activity_key,
            "answer_template": self.answer_template,
        }
        ctx.update(self.extra_context)
        activity_completed.send(sender=self, activity_key=self.activity_key, activity_session_state=self.session_state, request=request)
        return render(request, self.completed_template_name, ctx)
