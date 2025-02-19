let questions = [];
let currentQuestionIndex = 0;
let score = 0;
let timeLeft = 120;
let timerInterval;

// Function to start the quiz
function startQuiz(level) {
    document.getElementById("level-selection").style.display = "none";
    document.getElementById("quiz-section").style.display = "block";
    fetchQuestions(level);
}

// Function to fetch questions from backend
const fetchQuestions = async (level) => {
    // Show loading message
    document.getElementById("loading").innerText = "Loading questions...";
    document.getElementById("loading").style.animation = "fadeIn 2s ease-in-out infinite, textAnimation 2s ease-in-out 2s infinite";

    document.getElementById("answer-buttons").innerHTML = ""; // Clear previous options


    fetch(`http://192.168.92.215:5001/get-questions?level=${level}`)
        .then(response => response.json())
        .then(data => {
            questions = data;
            document.getElementById("loading").style.display = "none";

            if (questions.length === 0) {
                document.getElementById("question-text").innerText = "No questions available.";
            } else {
                displayQuestion();
                startTimer();
            }
        })
        .catch(error => {
            console.error("Error fetching questions:", error);
            document.getElementById("question-text").innerText = "Failed to load questions. Please try again.";
        });
}

// Function to display a question
function displayQuestion() {
    if (currentQuestionIndex >= questions.length) {
        console.log("No more questions. Ending quiz.");
        endQuiz();
        return;
    }

    const currentQuestion = questions[currentQuestionIndex];
    document.getElementById("question-text").innerText = currentQuestion.question;
    
    const answerButtons = document.getElementById("answer-buttons");
    answerButtons.innerHTML = "";

    currentQuestion.options.forEach(option => {
        const button = document.createElement("button");
        button.innerText = option;
        button.onclick = () => {
            checkAnswer(option)
        };
        answerButtons.appendChild(button);
    });
    
    // alert("Displayed question")

}

// Function to check answer
function checkAnswer(selectedOption) {
    // document.querySelectorAll("#answer-buttons button").forEach(button => button.disabled = true);

    if (selectedOption === questions[currentQuestionIndex].correctAnswer) {
        score++;
    }
    currentQuestionIndex++;
    setTimeout(() => {
        try {
            displayQuestion();
        } catch (error) {
            console.error("Error in displaying question:", error);
        }
    }, 1000);
     // Show next question after a delay
}

// Function to start timer
function startTimer() {
    document.getElementById("timer").innerText = `Time Left: ${timeLeft}s`;
    
    
    timerInterval = setInterval(() => {
        timeLeft--;
        document.getElementById("timer").innerText = `Time Left: ${timeLeft}s`;

        if (timeLeft <= 0) {
            console.log("⏳ Time's up! Ending quiz.");
            endQuiz();
        }
    }, 1000);
}


// Function to end quiz
function endQuiz() {
    clearInterval(timerInterval);
    document.getElementById("quiz-section").innerHTML = `
        <h2>Quiz Completed!</h2>
        <p>Your Score: ${score} / ${questions.length}</p>
    `;
}
