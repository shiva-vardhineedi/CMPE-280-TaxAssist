let historyEnabled = false;

$(document).ready(function () {
    const userAvatar = 'https://on3static.com/uploads/assets/212/150/150212.svg'; // User avatar
    const botAvatar = 'https://i.pravatar.cc/40?img=2'; // Bot avatar

    // Load chat history from sessionStorage
    if (sessionStorage.getItem('chatHistory')) {
        $('#chat-box').html(sessionStorage.getItem('chatHistory'));
        $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight); // Scroll to bottom on load
    }

    const scrollBanner = $("#scroll-banner");

    // Check if user is scrolled to the bottom
    function isScrolledToBottom() {
        const chatBox = $("#chat-box")[0];
        return chatBox.scrollHeight - chatBox.scrollTop === chatBox.clientHeight;
    }

    // Show scroll-to-bottom banner if not scrolled
    function handleNewMessage() {
        if (!isScrolledToBottom()) {
            scrollBanner.show(); // Show the scroll banner
        } else {
            scrollBanner.hide(); // Hide the banner if already at the bottom
        }
    }

    // Scroll to bottom when banner is clicked
    scrollBanner.click(function () {
        $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight);
        scrollBanner.hide(); // Hide the banner after scrolling
    });

    // Handle history toggle
    $("#history-toggle").change(function () {
        historyEnabled = $(this).is(':checked');
        if (historyEnabled) {
            // Fetch the last 5 entries from the database and display them
            $.ajax({
                type: "GET",
                url: "http://127.0.0.1:8000/get-history",  // Endpoint for fetching history
                success: function (data) {
                    if (data && data.history && data.history.length > 0) {
                        let historyHtml = '';
                        data.history.forEach(entry => {
                            // Format user prompt
                            historyHtml += `
                                <div class="message user">
                                    <img src="${userAvatar}" class="avatar">
                                    <div class="message-content">${entry.prompt}</div>
                                </div>
                            `;
                            // Format assistant response
                            historyHtml += `
                                <div class="message assistant">
                                    <img src="${botAvatar}" class="avatar">
                                    <div class="message-content">${entry.response}</div>
                                </div>
                            `;
                        });
                        // Clear chat and display history
                        $("#chat-box").html(historyHtml);
                        $("#chat-box").scrollTop($("#chat-box")[0].scrollHeight); // Scroll to bottom
                    } else {
                        console.error("No history data received or invalid format:", data);
                    }
                },
                error: function (xhr, status, error) {
                    alert("Error fetching history. Please try again.");
                    console.error("Error details:", status, error);
                }
            });
        } else {
            // Clear the chat box if history is disabled
            $("#chat-box").empty();
        }
    });

    // Handle sending the message
    $("#send-button").click(function () {
        const userInput = $("#user-input").val();
        if (userInput.trim() === "") return;

        // Display the user's question with avatar
        const userMessage = `
            <div class="message user">
                <img src="${userAvatar}" class="avatar">
                <div class="message-content">${userInput}</div>
            </div>
        `;
        const messageElement = $(userMessage);
        $("#chat-box").append(messageElement);
        $("#user-input").val("");  // Clear the input

        // Make the user message visible with animation
        setTimeout(() => {
            messageElement.css({
                opacity: 1,
                transform: 'translateY(0)'
            });
        }, 10);

        updateSessionStorage();
        handleNewMessage();  // Check if user is at the bottom

        // Add loading indicator
        const loadingMessage = `
            <div class="message assistant" id="loading-indicator">
                <img src="${botAvatar}" class="avatar">
                <div class="message-content"><div class="loading"><div></div><div></div><div></div></div></div>
            </div>
        `;
        const loadingElement = $(loadingMessage);
        $("#chat-box").append(loadingElement);

        // Make the loading message visible with animation
        setTimeout(() => {
            loadingElement.css({
                opacity: 1,
                transform: 'translateY(0)'
            });
        }, 10);

        // Send the question to the backend via AJAX, passing history state
        const apiUrl = historyEnabled 
            ? "http://127.0.0.1:8000/get-tax-response?history=true"
            : "http://127.0.0.1:8000/get-tax-response";

        $.ajax({
            type: "POST",
            url: apiUrl,
            contentType: "application/json",
            data: JSON.stringify({ "user_input": userInput }),
            success: function (response) {
                // Remove loading indicator
                $("#loading-indicator").remove();

                // Beautify the assistant's response with formatting
                const formattedResponse = response.response
                    .replace(/\n/g, '<br>')
                    .replace(/(?:^|\s)(\d\.)/g, '<br>$1') // Format ordered lists
                    .replace(/\*(.*?)\*/g, '<strong>$1</strong>'); // Bold for emphasis

                // Display the assistant's response with avatar and formatting
                const assistantMessage = `
                    <div class="message assistant">
                        <img src="${botAvatar}" class="avatar">
                        <div class="message-content">${formattedResponse}</div>
                    </div>
                `;
                const assistantElement = $(assistantMessage);
                $("#chat-box").append(assistantElement);

                // Make the assistant's message visible with animation
                setTimeout(() => {
                    assistantElement.css({
                        opacity: 1,
                        transform: 'translateY(0)'
                    });
                }, 10);

                updateSessionStorage();
                handleNewMessage();  // Check if user is at the bottom
            },
            error: function () {
                $("#loading-indicator").remove(); // Remove loading indicator in case of error
                alert("Error communicating with the server. Please try again.");
            }
        });
    });

    // Press Enter to send the message
    $("#user-input").keypress(function (e) {
        if (e.which === 13) {
            $("#send-button").click();
        }
    });

    // Update sessionStorage with the current chat history
    function updateSessionStorage() {
        sessionStorage.setItem('chatHistory', $('#chat-box').html());
    }

    // Clear session storage on window close
    $(window).on('beforeunload', function () {
        sessionStorage.removeItem('chatHistory');
    });
});
