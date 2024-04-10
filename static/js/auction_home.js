let homeSocket = new WebSocket(`ws://${window.location.host}/ws/`);
    homeSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        console.log('Home Data', data);

        if (data.type === 'time_update') {
            const auctionId = data.auction_id;
            const remainingTime = data.remaining_time;
            // Update the countdown using the function
            updateCountdown(auctionId, remainingTime);
            updateCountdown2(auctionId, remainingTime);
        }
        

    };

    function updateCountdown(auctionId, remainingTime) {
        const countdownElement = document.getElementById(`countdown_${auctionId}`);


        // Set up a new interval to update the countdown every second
        const countdownInterval = setInterval(function () {
            const days = Math.floor(remainingTime / (60 * 60 * 24));
            const hours = Math.floor((remainingTime % (60 * 60 * 24)) / (60 * 60));
            const minutes = Math.floor((remainingTime % (60 * 60)) / 60);
            const seconds = Math.floor(remainingTime % 60);

            // Use the pad function to ensure consistent two-digit formatting
            const pad = (num) => (num < 10 ? `0${num}` : num);

            // Format the time components with consistent two-digit formatting
            const formattedTime = `${pad(days)}d ${pad(hours)}h ${pad(minutes)}m ${pad(seconds)}s`;

            // Update the countdown with the formatted time
            if(countdownElement){
                countdownElement.textContent = `Time left: ${formattedTime}`;
            }
            

            // Decrease the remaining time by one second
            remainingTime--;

            // Stop the interval when remainingTime reaches 0
            if (remainingTime < 0) {
                clearInterval(countdownInterval);
            }
        }, 1000); // Update every second
    }
    function updateCountdown2(auctionId, remainingTime) {
        const countdownElement = document.getElementById(`countdown2_${auctionId}`);


        // Set up a new interval to update the countdown every second
        const countdownInterval = setInterval(function () {
            const days = Math.floor(remainingTime / (60 * 60 * 24));
            const hours = Math.floor((remainingTime % (60 * 60 * 24)) / (60 * 60));
            const minutes = Math.floor((remainingTime % (60 * 60)) / 60);
            const seconds = Math.floor(remainingTime % 60);

            // Use the pad function to ensure consistent two-digit formatting
            const pad = (num) => (num < 10 ? `0${num}` : num);

            // Format the time components with consistent two-digit formatting
            const formattedTime = `${pad(days)}d ${pad(hours)}h ${pad(minutes)}m ${pad(seconds)}s`;

            // Update the countdown with the formatted time
            countdownElement.textContent = `Time left: ${formattedTime}`;

            // Decrease the remaining time by one second
            remainingTime--;

            // Stop the interval when remainingTime reaches 0
            if (remainingTime < 0) {
                clearInterval(countdownInterval);
            }
        }, 1000); // Update every second
    }