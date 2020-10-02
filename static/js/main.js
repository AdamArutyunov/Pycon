function rate_news(news_id, rate) {
    if (rate === 1) {
        let button = document.getElementById("rate-up-" + news_id.toString())
        button.classList.add("rating-up")
        button.onclick = function() {
            unrate_news(news_id)
        }

        let other_button = document.getElementById("rate-down-" + news_id.toString())
        other_button.classList.remove("rating-down")
        other_button.onclick = function() {
            rate_news(news_id, -1)
        }

    } else if (rate === -1) {
        let button = document.getElementById("rate-down-" + news_id.toString())
        button.classList.add("rating-down")
        button.onclick = function() {
            unrate_news(news_id)
        }

        let other_button = document.getElementById("rate-up-" + news_id.toString())
        other_button.classList.remove("rating-up")
        other_button.onclick = function() {
            rate_news(news_id, 1)
        }
    }
    $.ajax({
        url: "/api/rate_news",
        method: "POST",
        contentType: 'application/json',
        data: JSON.stringify({"news_id": news_id, "rate": rate})
    }).done(function(data) {
        let counter = document.getElementById("rating-counter-" + news_id.toString())
        counter.innerHTML = data["new_rating"]
    })
}

function unrate_news(news_id) {
    $.ajax({
        url: "/api/unrate_news",
        method: "POST",
        contentType: 'application/json',
        data: JSON.stringify({"news_id": news_id})
    }).done(function(data) {
        let counter = document.getElementById("rating-counter-" + news_id.toString())
        counter.innerHTML = data["new_rating"]
    })

    let up_button = document.getElementById("rate-up-" + news_id.toString())
    let down_button = document.getElementById("rate-down-" + news_id.toString())

    up_button.onclick = function() {
        rate_news(news_id, 1)
    }
    up_button.classList.remove("rating-up")

    down_button.onclick = function() {
        rate_news(news_id, -1)
    }
    down_button.classList.remove("rating-down")
}