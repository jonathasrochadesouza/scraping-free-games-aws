function discoverGames() {
    const emailInput = document.getElementById('emailInput');
    const email = emailInput.value.trim();

    if (email === '') {
        alert('Por favor, insira seu email!');
        return;
    }

    if (!isValidEmail(email)) {
        alert('Por favor, insira um email válido!');
        return;
    }

    // IMPORTANT: Replace 'YOUR_LAMBDA_URL_HERE' with your actual AWS Lambda Function URL
    // The Lambda is necessary because Epic Games API doesn't allow direct CORS requests from browsers
    const lambdaUrl = 'https://ngch5oeejano2aym7ggtigol6i0hzuna.lambda-url.us-east-1.on.aws/';

    fetch(lambdaUrl, {
        method: 'GET'
    })
    .then(response => {
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Lambda already returns processed data in the correct format
        localStorage.setItem('gamesData', JSON.stringify(data));
        window.location.href = 'results.html';
    })
    .catch(error => {
        console.error('Error fetching games:', error);
        alert(`Erro ao buscar jogos: ${error.message}. Verifique o console para mais detalhes.`);
    });
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function goBack() {
    window.location.href = 'index.html';
}

// Permite enviar o formulário com Enter
document.addEventListener('DOMContentLoaded', function() {
    const emailInput = document.getElementById('emailInput');
    if (emailInput) {
        emailInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                discoverGames();
            }
        });
    }
});
