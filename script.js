document.addEventListener('DOMContentLoaded', () => {
    // Game variables
    const gameBoard = document.getElementById('game-board');
    const movesCount = document.getElementById('moves-count');
    const timeCounter = document.getElementById('time');
    const restartButton = document.getElementById('restart');

    let cards = [];
    let interval = null;
    let firstCard = false;
    let secondCard = false;
    let moves = 0;
    let seconds = 0;
    let minutes = 0;

    // Card symbols - using emojis for simplicity
    const symbols = ['🍎', '🍌', '🍇', '🍊', '🍓', '🍒', '🍑', '🥭'];

    // Initialize the game
    function initializeGame() {
        // Reset game variables
        cards = [];
        firstCard = false;
        secondCard = false;
        moves = 0;
        seconds = 0;
        minutes = 0;
        clearInterval(interval);

        // Reset UI
        movesCount.innerHTML = moves;
        timeCounter.innerHTML = "00:00";
        gameBoard.innerHTML = "";

        // Create card pairs
        const cardValues = [...symbols, ...symbols];

        // Shuffle cards
        cardValues.sort(() => Math.random() - 0.5);

        // Create card elements
        cardValues.forEach((value) => {
            cards.push(createCard(value));
        });

        // Add cards to the game board
        cards.forEach((card) => {
            gameBoard.appendChild(card);
        });

        // Start timer
        startTimer();
    }

    // Create a card element
    function createCard(value) {
        const card = document.createElement('div');
        card.classList.add('card');
        card.dataset.value = value;

        // Card front (with symbol)
        const frontFace = document.createElement('div');
        frontFace.classList.add('card-front');
        frontFace.innerHTML = value;

        // Card back (hidden)
        const backFace = document.createElement('div');
        backFace.classList.add('card-back');
        backFace.innerHTML = '?';

        // Add faces to card
        card.appendChild(frontFace);
        card.appendChild(backFace);

        // Add click event
        card.addEventListener('click', flipCard);

        return card;
    }

    // Flip a card
    function flipCard() {
        // If the card is already flipped or matched, do nothing
        if (this.classList.contains('flip') || this.classList.contains('matched')) {
            return;
        }

        // Flip the card
        this.classList.add('flip');

        // First card flipped
        if (!firstCard) {
            firstCard = this;
            return;
        }

        // Second card flipped
        secondCard = this;
        disableClicks();

        // Increment moves
        moves++;
        movesCount.innerHTML = moves;

        // Check if cards match
        checkForMatch();
    }

    // Disable clicking on cards during comparison
    function disableClicks() {
        cards.forEach(card => {
            card.style.pointerEvents = 'none';
        });
    }

    // Enable clicking on cards
    function enableClicks() {
        cards.forEach(card => {
            card.style.pointerEvents = 'auto';
        });
    }

    // Check if the two flipped cards match
    function checkForMatch() {
        const isMatch = firstCard.dataset.value === secondCard.dataset.value;

        if (isMatch) {
            // Match found
            firstCard.classList.add('matched');
            secondCard.classList.add('matched');

            // Check if all cards are matched
            checkGameCompletion();
        } else {
            // No match - flip cards back after a delay
            setTimeout(() => {
                firstCard.classList.remove('flip');
                secondCard.classList.remove('flip');
            }, 1000);
        }

        // Reset card selections
        setTimeout(() => {
            firstCard = false;
            secondCard = false;
            enableClicks();
        }, 1000);
    }

    // Check if all cards are matched
    function checkGameCompletion() {
        const matchedCards = document.querySelectorAll('.matched');

        if (matchedCards.length === cards.length) {
            clearInterval(interval);

            // Show completion message
            setTimeout(() => {
                const completionMessage = `Congratulations! You completed the game in ${moves} moves and ${minutes}:${seconds < 10 ? '0' + seconds : seconds}!`;
                alert(completionMessage);
            }, 500);
        }
    }

    // Start the timer
    function startTimer() {
        interval = setInterval(() => {
            seconds++;
            if (seconds === 60) {
                minutes++;
                seconds = 0;
            }

            // Update timer display
            timeCounter.innerHTML = `${minutes < 10 ? '0' + minutes : minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
        }, 1000);
    }

    // Restart button event
    restartButton.addEventListener('click', initializeGame);

    // Initialize the game on page load
    initializeGame();
});