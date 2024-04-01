from django.urls import path
from . import views
from .views import QuizList, QuizAnswer, QuizCreate, QuizListLoginView, RegisterQuizApp, QuizManage, QuizDetail, QuizEdit, QuizDelete, check_quiz_answer, reset_user_quiz_status, UserPage
from django.contrib.auth.views import LogoutView

urlpatterns = [
  path("", QuizList.as_view(), name="quizzes"),
  path("quiz/<int:pk>/", QuizAnswer.as_view(), name="quiz"),
  path("create-quiz/", QuizCreate.as_view(), name="create-quiz"),
  path("login/", QuizListLoginView.as_view(), name="login"),
  path("logout/", LogoutView.as_view(next_page='quizzes'), name="logout"),
  path("register/", RegisterQuizApp.as_view(), name="register"),
  path("manage/", QuizManage.as_view(), name="manage-quizzes"),
  path("detail/<int:pk>/", QuizDetail.as_view(), name="quiz-detail"),
  path("edit/<int:pk>/", QuizEdit.as_view(), name="quiz-edit"),
  path("delete/<int:pk>/", QuizDelete.as_view(), name="quiz-delete"),
  path("user/<str:username>/quizzes/", UserPage.as_view(), name="userpage"),
  path('quiz/<int:pk>/check_answer/', check_quiz_answer, name='check-quiz-answer'),
  path('reset/', reset_user_quiz_status, name='reset'),
]