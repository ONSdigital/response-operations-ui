(function(window) {
    function initDataPanels() {
        const acc = document.getElementsByClassName('data-panel-header');
        for (let i = 0; i < acc.length; i++) {
            const initPanel = acc[i].nextElementSibling;
            initPanel.style.display = 'none';

            // Add event listener to toggle displaying the data panel
            acc[i].addEventListener('click', function() {
                const panel = this.nextElementSibling;
                this.classList.toggle('active');
                if (panel.style.display === 'block') {
                    panel.style.display = 'none';
                } else {
                    panel.style.display = 'block';
                }
            });
        }
    }

    function openPanel() {
        const panelName = window.location.hash;
        if (panelName) {
            document.querySelectorAll('.data-panel-header').classList.addClass('active');
            document.querySelectorAll('.data-panel-body').style.display = 'block';
        }
    }

    window.initDataPanels = initDataPanels;
    window.openPanel = openPanel;
}(window));

