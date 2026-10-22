
from flask import Flask, request, render_template_string, session
import time

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret-key"

correct_password = "admin123"
LOCK_DURATION = 30

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Login</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #141e30, #243b55);
        }

        .login-box {
            width: 360px;
            max-width: 92%;
            padding: 35px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            text-align: center;
        }

        .icon {
            font-size: 48px;
            margin-bottom: 10px;
        }

        h2 {
            color: #1e293b;
            margin-bottom: 8px;
        }

        .subtitle {
            color: #64748b;
            font-size: 14px;
            margin-bottom: 25px;
        }

        input[type="password"],
        input[type="text"] {
            width: 100%;
            padding: 13px;
            margin-bottom: 15px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            outline: none;
            font-size: 15px;
        }

        input:focus {
            border-color: #2563eb;
            box-shadow: 0 0 5px #93c5fd;
        }

        .show-password {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 20px;
            color: #475569;
            font-size: 13px;
            text-align: left;
        }

        button {
            width: 100%;
            padding: 13px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
        }

        button:hover {
            background: #1d4ed8;
        }

        button:disabled {
            background: #94a3b8;
            cursor: not-allowed;
        }

        .message {
            margin-top: 18px;
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
        }

        .success {
            color: #166534;
            background: #dcfce7;
        }

        .error {
            color: #b91c1c;
            background: #fee2e2;
        }

        .info {
            margin-top: 18px;
            font-size: 13px;
            color: #64748b;
        }

        #timer {
            color: #dc2626;
            font-weight: bold;
            font-size: 22px;
        }
    </style>
</head>

<body>
    <div class="login-box">
        <div class="icon">🔐</div>

        <h2>Welcome Back!</h2>
        <p class="subtitle">Enter your password to continue</p>

        {% if not locked and not success %}
        <form method="POST">
            <input
                type="password"
                id="password"
                name="password"
                placeholder="Enter your password"
                required
                autofocus
            >

            <label class="show-password">
                <input type="checkbox" onclick="togglePassword()">
                Show password
            </label>

            <button type="submit">Login</button>
        </form>
        {% endif %}

        {% if message %}
        <div class="message {{ status }}">
            {{ message }}
        </div>
        {% endif %}

        {% if locked %}
        <p class="info">
            Try again in <span id="timer">{{ remaining_time }}</span> seconds
        </p>

        <script>
            let seconds = {{ remaining_time }};
            const timer = document.getElementById("timer");

            const countdown = setInterval(() => {
                seconds--;
                timer.textContent = Math.max(seconds, 0);

                if (seconds <= 0) {
                    clearInterval(countdown);
                    window.location.reload();
                }
            }, 1000);
        </script>

        {% elif not success %}
        <p class="info">
            Attempts remaining: {{ remaining }} / 3
        </p>
        {% else %}
        <p class="info">You are now logged in.</p>
        {% endif %}
    </div>

    <script>
        function togglePassword() {
            const password = document.getElementById("password");

            if (password) {
                password.type =
                    password.type === "password" ? "text" : "password";
            }
        }
    </script>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def login():
    if "attempts" not in session:
        session["attempts"] = 0

    if "lock_until" not in session:
        session["lock_until"] = 0

    message = ""
    status = ""
    success = session.get("success", False)
    current_time = time.time()

    # Check if the account is currently locked
    if current_time < session["lock_until"]:
        locked = True
        remaining_time = int(session["lock_until"] - current_time) + 1
        message = "Account locked! Too many failed attempts."
        status = "error"

    else:
        # Reset attempts after the lock duration
        if session["lock_until"] > 0:
            session["attempts"] = 0
            session["lock_until"] = 0

        locked = False
        remaining_time = 0

        if request.method == "POST" and not success:
            password = request.form.get("password", "")

            if password == correct_password:
                session["success"] = True
                success = True
                message = "Login successful!"
                status = "success"

            else:
                session["attempts"] += 1
                status = "error"

                if session["attempts"] >= 3:
                    session["lock_until"] = time.time() + LOCK_DURATION
                    locked = True
                    remaining_time = LOCK_DURATION
                    message = "Account locked! Too many failed attempts."
                else:
                    remaining = 3 - session["attempts"]
                    message = (
                        f"Wrong password! {remaining} attempt(s) remaining."
                    )

    remaining = max(0, 3 - session["attempts"])

    return render_template_string(
        HTML,
        message=message,
        status=status,
        remaining=remaining,
        locked=locked,
        success=success,
        remaining_time=remaining_time
    )


if __name__ == "__main__":
    app.run(debug=True)
