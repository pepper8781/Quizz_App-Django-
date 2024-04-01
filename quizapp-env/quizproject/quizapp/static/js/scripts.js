document.addEventListener("DOMContentLoaded", function(){

  const answersList = document.querySelectorAll('ol li');

  answersList.forEach(li => li.addEventListener('click', checkClickedAnswer));

  let isAnswered = false;

  function checkClickedAnswer(event){
    if(isAnswered){
      return;
    }

    const clickedAnswerElement = event.currentTarget;

    const selectedAnswer = clickedAnswerElement.dataset.answer;

    const resultSpan = clickedAnswerElement.querySelector('.result');

    const questionID = clickedAnswerElement.closest('ol.answers').dataset.id;

    fetch(`/quiz/${questionID}/check_answer/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),  // CSRFトークンを取得
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `selectedAnswer=${selectedAnswer}`
    })
    .then(response => response.json())
    .then(data => {
      const result = data.result;

      const correctAnswer = data.correctAnswer;

      const explanation = data.explanation;

      displayResult(result, clickedAnswerElement, resultSpan, correctAnswer, explanation);

    })
    .catch(error => {
      console.error('Error:', error);
    });

    isAnswered = true;

    if (isAnswered) {
      answersList.forEach(answer => {
        answer.classList.add('no-hover');
      });
    }
  }

  function displayResult(result, clickedAnswerElement, resultSpan, correctAnswer, explanation){
    if (result) {
      resultSpan.textContent = '〇';
      resultSpan.style.color = 'red';
      document.querySelector('.answer').innerHTML = correctAnswer;
      document.querySelector('.explanation').innerHTML = explanation;
      clickedAnswerElement.querySelector(".answer-text").style.color = 'red'
      resultSpan.style.display = 'inline';
      // isCorrected[questionID] = true;
      document.querySelector('.comment').style.display = 'block';
    } else {
      resultSpan.textContent = '×';
      resultSpan.style.color = 'blue';
      clickedAnswerElement.querySelector(".answer-text").style.color = 'blue';
      resultSpan.style.display = 'inline';
      document.querySelector('.onemore').style.display = 'block';
    }

  }


  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  const modal = document.querySelector('.resetModal');

  const openRetry = document.querySelector('.retry');  

  const reset = document.querySelector('.reset');

  const closeModalButton = document.querySelector('.cancel');

  openRetry.addEventListener('click', openModal);

  closeModalButton.addEventListener('click', closeModal);

  function openModal() {
    modal.style.display = 'flex';
    //背景をクリックできないようにするためのカバー
    document.querySelector('.cover').style.display = 'block';
  }

  function closeModal() {
    modal.style.display = 'none';
    document.querySelector('.cover').style.display = 'none';
  }

  reset.addEventListener('click', resetData);

  function resetData() {
      fetch('/reset/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'), 
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })
      .then(response => {
        if (response.ok) {
          // レスポンスが成功した場合、ページをリロードする
          window.location.reload();
        } else {
          // レスポンスが失敗した場合、エラーを投げる
          throw new Error('Network response was not ok.');
        }
      })
      .catch(error => console.error('Error:', error));
    }

  }
);