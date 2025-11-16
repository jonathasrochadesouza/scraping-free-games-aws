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
    
    // Redireciona para a página de resultados
    window.location.href = 'results.html';
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
