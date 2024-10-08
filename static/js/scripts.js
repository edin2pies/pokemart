document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

const themeToggleButton = document.getElementById('themeToggleButton');
themeToggleButton.addEventListener('click', () => {
    document.body.classList.toggle('dark-theme');
});

fetch('/api/pokemon')
    .then(response => response.json())
    .then(data => {
        const select = document.getElementById("pokemon-name");
        data.forEach(pokemon => {
            const option = document.createElement("option");
            option.value = pokemon.name;
            option.textContent = pokemon.name;
            select.appendChild(option);
            
            // Populate descriptions
            pokemonDescriptions[pokemon.name] = pokemon;
        });
    });