$(document).ready(function () {


    // ****** Scoket changes code

    var socket = io.connect('http://' + document.domain + ':' + location.port);

    let speaking = false;
    let synth = window.speechSynthesis;
    let utterance = new SpeechSynthesisUtterance();
    var audio = new Audio("../static/music.wav");


    socket.on('connect', function () {
        console.log('Connected to the server.');
    });


    socket.on('alert_event', function (data) {
        console.log('Received a custom event:', data);

        if (data == 1) {
  
            document.getElementById('AirAnimation').classList.add('hidden')
            document.getElementById('StopAlert').classList.remove('hidden')
            utterance.text = "Please open your eyes";
            synth.speak(utterance);
            audio.play();

        }
        else {
            document.getElementById('StopAlert').classList.add('hidden')
            document.getElementById('AirAnimation').classList.remove('hidden')
            synth.cancel();
            audio.pause();
        }

        // Handle the data received from the server
    });


    // ******* fucntion to start and stop air animation and camera image change

    // Function to update content based on the current route
    function updateContent(route) {
        // Example: Update content based on different routes
        if (route === '/') {
            document.getElementById('AirAnimation').classList.add('hidden')
            document.getElementById('VideoImage').src = "../static/hello.jpg"
        } else if (route === '/start_stream') {
            document.getElementById('AirAnimation').classList.remove('hidden')
        } else {
            document.getElementById('AirAnimation').classList.add('hidden')
            document.getElementById('VideoImage').src = "../static/hello.jpg"
        }
    }

    // Initial update on page load
    updateContent(window.location.pathname);

    // Listen for changes in the browser's URL (route changes)
    $(window).on('popstate', function () {
        // Update content when the route changes
        updateContent(window.location.pathname);
    });


    // ******* Function to change the date and time
    const today = new Date();
    const yyyy = today.getFullYear();
    let mm = today.toLocaleString('default', { month: 'long' }); // Months start at 0!
    let dd = today.getDate();

    document.getElementById("MainDate").innerHTML = mm + " " + dd + " " + yyyy;
    document.getElementById("MainTime").innerHTML = today.toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true });





});