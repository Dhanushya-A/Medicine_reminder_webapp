
// ==========================
// DARK MODE
// ==========================

const darkBtn = document.getElementById("darkBtn");

// Load saved theme
if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark-mode");
}

if (darkBtn) {

    darkBtn.addEventListener("click", function () {

        document.body.classList.toggle("dark-mode");

        // Save theme
        if (document.body.classList.contains("dark-mode")) {
            localStorage.setItem("theme", "dark");
        } else {
            localStorage.setItem("theme", "light");
        }

    });

}


// SEARCH

const searchInput = document.getElementById(
    "searchInput"
);

if(searchInput){

    searchInput.addEventListener(
        "keyup",

        function(){

            let value =
            this.value.toLowerCase();

            let cards =
            document.querySelectorAll(
                ".medicine-card"
            );

            cards.forEach(card => {

                let text =
                card.innerText.toLowerCase();

                if(text.includes(value)){

                    card.style.display =
                    "block";

                }

                else{

                    card.style.display =
                    "none";

                }

            });

        }

    );

}




// ==========================
// VOICE REMINDER
// ==========================

function speakMedicine(name,time){

    let text =

    "Hello. It is time to take your medicine " +

    name +

    ". Scheduled time is " +

    time;

    let speech =
    new SpeechSynthesisUtterance(
        text
    );

    speech.volume = 1;

    speech.rate = 1;

    speech.pitch = 1;

    speech.lang = "en-US";

    window.speechSynthesis.speak(
        speech
    );

}



// ==========================
// AUTO TIME CHECK
// ==========================

function checkMedicineReminder(){

    let now = new Date();

    let currentHour =
    String(now.getHours())
    .padStart(2,'0');

    let currentMinute =
    String(now.getMinutes())
    .padStart(2,'0');

    let currentTime =
    currentHour +
    ":" +
    currentMinute;

    let cards =
    document.querySelectorAll(
        ".medicine-card"
    );

    cards.forEach(card => {

        let medicineName =

        card.querySelector(
            ".medicine-name"
        ).innerText;

        let medicineTime =

        card.querySelector(
            ".medicine-time"
        ).innerText
        .replace("⏰","")
        .trim();



        if(currentTime === medicineTime){

            speakMedicine(
                medicineName,
                medicineTime
            );

        }

    });

}



// CHECK EVERY 30 SECONDS

setInterval(
    checkMedicineReminder,
    30000
);

