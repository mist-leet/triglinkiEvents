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

    updateCards: function (parseddata) {
        for (let i = 1; i <= 3; i++) {
            let current_container = `#event${i}`
            this.updateCard($(current_container), parseddata[i - 1], i);
        }
    },

    updateCard: function (event_card, data, number) {
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
        content.contents()[0].data = data.text;

        let timeDate = content.find('.date');
        let timeStart = content.find('.start');
        let timeEnd = content.find('.end');

        let dataStartDate = new Date(data.dtstart);
        let dataEndDate =   new Date(data.dtend);

        timeDate.text(this.formatDateToDate(dataStartDate));
        timeStart.text(this.formatDateToTime(dataStartDate));
        timeEnd.text(this.formatDateToTime(dataEndDate));

    },

    formatDateToDate: function (d) {
        return ("0" + d.getDate()).slice(-2) + "." + ("0"+(d.getMonth()+1)).slice(-2) + "." +  d.getFullYear();
    },

    formatDateToTime: function (d) {
        return d.getHours() + ":" + (d.getMinutes() + "0").slice(-2);
    }
}
$( document ).ready(function() {
    eventCardUpdater.update()
});