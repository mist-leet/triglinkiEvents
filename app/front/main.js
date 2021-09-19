eventCardUpdater = {
    mainThread: $("#event_thread"),

    update: function () {
        console.log('updating...')
        this.getDataFromServer();
        setInterval(this.getDataFromServer.bind(this), 1000 * 60 * 60 * 3);
    },

    getDataFromServer: function () {
        $.ajax({
            url: "http://0.0.0.0:8080/get_events",
            type: 'get',
            success: function (data) {
                console.log(data);
                this.updateCards(data)
            }.bind(this),
            error: function (data) {
                console.log(data);
                console.log('cant get')
                this.getDataFromServer();
            }.bind(this)
        })
    },

    updateCards: function (parsedData) {
        for (let i = 0; i < parsedData.length; i++) {
            let current_container = `#event${i}`

            var parent = $('.event_card_container.columns');
            parent.append(this.getCardTemplate(i));

            this.updateCard($(current_container), parsedData[i]);
        }
        animator.startAnimation();
    },

    getCardTemplate: function (number) {
        return `<div id="event${number}" class="column event">
            <div class="card">
                <div class="card-image">
                    <figure class="image">
                        <img src="placeholder.jpg" class="card_image"
                             alt="Placeholder image">
                    </figure>
                </div>
                <div class="card-content">
                    <div class="media-content">
                        <p class="title is-3 card_title"></p>
                    </div>

                    <div class="content in_card_content">
                        <strong><time class="date"></time></strong>
                        <br>
                        <strong>
                            <time class="start"></time>
                            -
                            <time class="end"></time>
                        </strong>
                        <p class="text-content">
                        </p>
                    </div>
                </div>
            </div>
        </div>`
    },

    updateCard: function (event_card, data) {
        if (!data) {
            return;
        }
        let card = event_card.find('.card');

        let card_image = card.find('.card-image');
        let card_content = card.find('.card-content');

        let image_elem = card_image.find('img')[0];
        if (data.picture) {
            image_elem.src = data.picture;
        } else {
            image_elem.src = 'placeholder.jpg'
        }


        let title = card_content.find('.title');
        title.text(data.name);

        let content = card_content.find('.content');
        content.find('.text-content').text(data.text);

        let timeDate = content.find('.date');
        let timeStart = content.find('.start');
        let timeEnd = content.find('.end');

        let dataStartDate = new Date(data.dtstart);
        let dataEndDate = new Date(data.dtend);

        timeDate.text(this.formatDateToDate(dataStartDate));
        timeStart.text(this.formatDateToTime(dataStartDate));
        timeEnd.text(this.formatDateToTime(dataEndDate));

    },

    formatDateToDate: function (d) {
        return ("0" + d.getDate()).slice(-2) + "." + ("0" + (d.getMonth() + 1)).slice(-2) + "." + d.getFullYear();
    },

    formatDateToTime: function (d) {
        return d.getHours() + ":" + (d.getMinutes() + "0").slice(0, 2);
    }
}

timeUpdater = {
    dateElement: $('.date_date'),
    timeElement: $('.date_time'),

    updateTime: function () {
        var today = new Date();

        var date = today.getDate() + '.' + (today.getMonth() + 1) + '.' + today.getFullYear();
        var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();

        this.dateElement.innerHTML = date;
        this.timeElement.innerHTML = time;
    },

    startUpdate: function () {
        this.dateElement = $('.date_date')[0];
        this.timeElement = $('.date_time')[0];

        setInterval(this.updateTime.bind(this), 1000);
    },
}

animator = {
    startAnimation: function () {
        this.animateCards();
    },

    animateCards: function () {
        console.log('animante!!!');
        let count = $('.event').length;
        let time = count * 500;
        let max_scroll = $('#event_thread')[0].scrollWidth;

        setTimeout(this.animateCards.bind(this), time * 2);

        $('#event_thread').animate({scrollLeft: max_scroll}, time);
        $('#event_thread').animate({scrollLeft: 0}, time);
    }
}

$(document).ready(function () {
    timeUpdater.startUpdate();
    eventCardUpdater.update();
    //animator.startAnimation();
});



