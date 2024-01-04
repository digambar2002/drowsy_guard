$(document).ready(function () {


    // ****** Scoket changes code

    var socket = io.connect('https://' + document.domain + ':' + location.port);
    socket.on('connect', function () {
        console.log('Connected to the server.');
    });

    let speaking = false;
    let synth = window.speechSynthesis;
    let utterance = new SpeechSynthesisUtterance();
    var audio = new Audio("../static/music.wav");

    var canvas = document.getElementById("canvas");
    var context = canvas.getContext("2d");
    const video = document.querySelector("#videoElement");

    var highway = document.getElementById('HighWay');
    highway.style.animationPlayState = 'paused';

    video.width = 400;
    video.height = 300;

    let videoStream;

    document.getElementById('AirAnimation').classList.add('hidden')
    document.getElementById('photo').hidden = true


    $("#StartBtn").click(function () {

        document.getElementById('StopAlert').classList.add('hidden')
        document.getElementById('AirAnimation').classList.remove('hidden')
        document.getElementById('photo').hidden = false
        document.getElementById('cover').hidden = true
        highway.style.animationPlayState = 'running';
        if (navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices
                .getUserMedia({
                    video: true,
                })
                .then(function (stream) {
                    videoStream = stream;
                    video.srcObject = stream;
                    video.play();
                })
                .catch(function (err0r) { });
        }

        const FPS = 10;
        setInterval(() => {
            let width = video.width;
            let height = video.height;
            context.drawImage(video, 0, 0, width, height);
            var data = canvas.toDataURL("image/jpeg", 0.5);
            context.clearRect(0, 0, width, height);
            socket.emit("image", data);
        }, 1000 / FPS);

        socket.on("processed_image", function (image) {
            photo.setAttribute("src", image);
        });

        // Start timer
        if (!isTimerRunning) {
            if (isTimerPaused()) {
                // Resume the timer from the paused time
                startTime += Date.now() - pausedTime;
                pausedTime = 0;
            } else {
                // Start the timer from the beginning
                startTime = Date.now();
            }

            isTimerRunning = true;
            setInterval(updateTimerAndDistance, 1000);
        }

    });

    $("#StopBtn").click(function () {

        document.getElementById('AirAnimation').classList.add('hidden')
        document.getElementById('photo').hidden = true
        document.getElementById('cover').hidden = false
        highway.style.animationPlayState = 'paused';

        if (videoStream) {
            // Get all tracks from the stream
            const tracks = videoStream.getTracks();

            // Stop each track
            tracks.forEach(track => track.stop());

            // Reset the video source object
            video.srcObject = null;

            // Set the videoStream variable to null
            videoStream = null;
        }

        // Stop timmer
        if (isTimerRunning) {
            pausedTime = Date.now();
            isTimerRunning = false;
        }

    });






    socket.on('alert', function (data) {
        console.log('Received a custom event:', data);

        if (data == 1) {

            document.getElementById('AirAnimation').classList.add('hidden')
            document.getElementById('StopAlert').classList.remove('hidden')
            highway.style.animationPlayState = 'paused';
            utterance.text = "Please open your eyes";
            synth.speak(utterance);
            audio.play();

        }
        else {
            highway.style.animationPlayState = 'running';
            document.getElementById('StopAlert').classList.add('hidden')
            document.getElementById('AirAnimation').classList.remove('hidden')
            synth.cancel();
            audio.pause();
        }

        // Handle the data received from the server
    });


    // ******* Function to change the date and time
    const today = new Date();
    const yyyy = today.getFullYear();
    let mm = today.toLocaleString('default', { month: 'long' }); // Months start at 0!
    let dd = today.getDate();

    document.getElementById("MainDate").innerHTML = mm + " " + dd + " " + yyyy;
    document.getElementById("MainTime").innerHTML = today.toLocaleString('en-US', { hour: 'numeric', minute: 'numeric', hour12: true });


    // Variables
    let distance = 0;
    let startTime = 0;
    let pausedTime = 0;
    let isTimerRunning = false;

    // Elements
    const timerElement = document.getElementById("DrivingTime");
    const distanceElement = document.getElementById("DrivingDistance");


    // Function to update time and distance
    function updateTimerAndDistance() {
        if (isTimerRunning) {
            const currentTime = Date.now();
            const elapsedPausedTime = isTimerPaused() ? currentTime - pausedTime : 0;
            const totalTimeElapsed = currentTime - startTime - elapsedPausedTime;
            const minutes = Math.floor(totalTimeElapsed / (1000 * 60));
            const seconds = Math.floor((totalTimeElapsed % (1000 * 60)) / 1000);

            timerElement.textContent = `${minutes} : ${seconds}`;

            // Check if 5 minutes have passed and increment the distance variable
            if (minutes % 5 === 0 && seconds === 0) {
                distance += 1;
                distanceElement.textContent = `${distance}`;
            }
        }
    }

    // Function to check if the timer is paused
    function isTimerPaused() {
        return pausedTime > 0;
    }


});