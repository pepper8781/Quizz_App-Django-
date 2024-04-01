from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from quizapp.models import Quiz, UserQuizStatus

# Create your views here.
class QuizList(ListView):
  model = Quiz
  context_object_name = "quizzes"
  def get_queryset(self):
    filter_option = self.request.GET.get('filter', 'all')
    
    # ログイン中のユーザーを取得
    user = self.request.user

    if filter_option == 'unanswered' and user.is_authenticated:
        # 未正答の問題をフィルタリング
        answered_quiz_ids = UserQuizStatus.objects.filter(
            user=user, is_correct=True
        ).values_list('quiz_id', flat=True)
        queryset = Quiz.objects.exclude(id__in=answered_quiz_ids)
    else:
        # 全問題
        queryset = Quiz.objects.all()

    return queryset

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)

    searchInputText = self.request.GET.get('search') or ""

    if searchInputText:
        context["quizzes"] = context["quizzes"].filter(
          Q(title__icontains=searchInputText) |
          Q(statement__icontains=searchInputText) |
          Q(user__username__startswith=searchInputText)
        )
    
    total_quizzes = Quiz.objects.count()
    context['total_quizzes'] = total_quizzes

    if self.request.user.is_authenticated:
        total_quizzes = Quiz.objects.count()
        context['total_quizzes'] = total_quizzes
        correct_answers_count = UserQuizStatus.objects.filter(user=self.request.user, is_correct=True).count()
        context['correct_answers_count'] = correct_answers_count
        accuracy = (correct_answers_count / total_quizzes) * 100
        context['accuracy'] = round(accuracy, 1)
        correct_quizzes = UserQuizStatus.objects.filter(user=self.request.user, is_correct=True).values_list('quiz_id', flat=True)
        context['correct_quizzes'] = list(correct_quizzes)

    return context
     
class QuizAnswer(DetailView):
  model = Quiz
  context_object_name = 'quiz'
  template_name = "quizapp/quiz_answer.html"

class QuizCreate(LoginRequiredMixin, CreateView):
  model = Quiz
  fields = ["title", "statement", "answer_a", "answer_b", "answer_c", "answer_d", "correct_answer", "explanation"]
  success_url = reverse_lazy('manage-quizzes')

  def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class QuizListLoginView(LoginView):
    fields = "__all__"
    template_name = "quizapp/login.html"

    def get_success_url(self):
        return reverse_lazy("quizzes")

class RegisterQuizApp(FormView):
    template_name = "quizapp/register.html"
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        
        return super().form_valid(form)
    
class QuizManage(LoginRequiredMixin, ListView):
  model = Quiz
  context_object_name = "myQuizzes"
  template_name = "quizapp/quiz_manage.html"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["myQuizzes"] = context["myQuizzes"].filter(user=self.request.user)

    searchInputText = self.request.GET.get('search') or ""

    if searchInputText:
        context["myQuizzes"] = context["myQuizzes"].filter(title__startswith=searchInputText)

    return context

class QuizDetail(LoginRequiredMixin, DetailView):
  model = Quiz
  context_object_name = 'quiz'
  template_name = "quizapp/quiz_detail.html"

class QuizEdit(LoginRequiredMixin, UpdateView):
    model = Quiz
    fields = "__all__"
    template_name = "quizapp/quiz_edit.html"
    def get_success_url(self):
        # 編集が完了したクイズのIDを取得
        quiz_id = self.object.id
        # 'quiz-detail'ビューに対応するURLを生成して返す
        return reverse_lazy('quiz-detail', kwargs={'pk': quiz_id})

class QuizDelete(LoginRequiredMixin, DeleteView):
    model = Quiz
    template_name = "quizapp/quiz_delete.html"
    success_url = reverse_lazy('manage-quizzes')
    context_object_name = "quiz"

class UserPage(ListView):
    model = Quiz
    template_name = "quizapp/user_page.html"

    def get_queryset(self):
        username = self.kwargs.get('username')
        user_quizzes = None
        if username:
            user = User.objects.get(username=username)
            self.user_quizzes = Quiz.objects.filter(user=user)
            return self.user_quizzes
        else:
            return Quiz.objects.none()
    
    def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)

      searchInputText = self.request.GET.get('search') or ""

      if searchInputText:
          context["quizzes"] = context["quizzes"].filter(
            Q(title__icontains=searchInputText) |
            Q(statement__icontains=searchInputText) |
            Q(user__username__startswith=searchInputText)
          )

      if self.request.user.is_authenticated:
          user_quizzes = self.get_queryset()
          
          quiz_ids = user_quizzes.values_list('id', flat=True)

          quizzes_count = self.user_quizzes.count()
          context['total_quizzes'] = quizzes_count
          correct_answers_count = UserQuizStatus.objects.filter(
            user=self.request.user, 
            is_correct=True, 
            quiz_id__in=quiz_ids
          ).count()
          context['correct_answers_count'] = correct_answers_count
          accuracy = (correct_answers_count / quizzes_count) * 100
          context['accuracy'] = round(accuracy, 1)
          correct_quizzes = UserQuizStatus.objects.filter(user=self.request.user, is_correct=True).values_list('quiz_id', flat=True)
          context['correct_quizzes'] = list(correct_quizzes)

      return context


@require_POST
def check_quiz_answer(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    selected_answer = request.POST.get('selectedAnswer')
    is_correct = (selected_answer == quiz.correct_answer)
    data = {
          'result': is_correct,
          'correctAnswer': quiz.correct_answer,
          'explanation': quiz.explanation
      }
    if request.user.is_authenticated:
      quiz.total_submissions += 1
      if is_correct:
          quiz.correct_submissions += 1
      quiz.save()
      user_status, created = UserQuizStatus.objects.get_or_create(
          user=request.user,
          quiz=quiz
      )
      user_status.is_correct = is_correct
      user_status.save()
    return JsonResponse(data)

@require_POST
@login_required
def reset_user_quiz_status(request):

    UserQuizStatus.objects.filter(user=request.user).delete()

    return JsonResponse({'message': '回答状況がリセットされました。'})

  