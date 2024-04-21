from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    ANSWER_CHOICES = [
        ('A', 'Answer A'),
        ('B', 'Answer B'),
        ('C', 'Answer C'),
        ('D', 'Answer D'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    statement = models.TextField(null=True, blank=True)
    answer_a = models.CharField(max_length=30)
    answer_b = models.CharField(max_length=30)
    answer_c = models.CharField(max_length=30)
    answer_d = models.CharField(max_length=30)
    correct_answer = models.CharField(max_length=1, choices=ANSWER_CHOICES)
    explanation = models.TextField(null=True, blank=True)
    createdDate = models.DateTimeField(auto_now_add=True)
    correct_submissions = models.IntegerField(default=0)
    total_submissions = models.IntegerField(default=0)
    @property
    def accuracy_rate(self):
        if self.total_submissions > 0:
            rate = (self.correct_submissions / self.total_submissions) * 100
            return round(rate, 1)
        else:
            return 0.0

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["createdDate"]
        

class UserQuizStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

