easterEgg();

function easterEgg() {
    window.addEventListener('load', function () {
        setOnClick();
        allLinksClicked();
    })
}

function setOnClick() {
    // Get links to core tutorials
    var links = document.querySelectorAll('a[href*="tutorial_"]');
    var tutorialLinks = Array.from(links).filter(link => /tutorial_[01]\d*/.test(link.getAttribute('href')));

    tutorialLinks.forEach(link => {
        link.setAttribute('onclick','tutorialClicked(this)')
    });
}

function allLinksClicked() {
    var clickedLinks = JSON.parse(sessionStorage.getItem('clickedLinks')) || [];
    if (clickedLinks.length >= 13) {
        // Select the container element
        const wyNavContent = document.querySelector('.bd-content');

        // Create two waves
        var waveDiv = document.createElement('div');
        waveDiv.className = 'wave';
        var waveDiv2 = document.createElement('div');
        waveDiv2.className = 'wave';

        // Insert waves into container
        wyNavContent.insertBefore(waveDiv, wyNavContent.firstChild);
        wyNavContent.insertBefore(waveDiv2, wyNavContent.firstChild);
    }
}

function tutorialClicked(element) {
    const href = element.getAttribute('href');
    var clickedLinks = JSON.parse(sessionStorage.getItem('clickedLinks')) || [];
    if (!clickedLinks.includes(href)) {
        // Store the clicked link in sessionStorage
        clickedLinks.push(href);
        sessionStorage.setItem('clickedLinks', JSON.stringify(clickedLinks));
    }
}

