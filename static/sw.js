self.addEventListener("push", function (event) {
    const data = event.data.json();

    const options = {
        body: data.body,
        icon: "/static/icon.png",
        data: {
            url: "/" // URL mở khi click vào thông báo
        }
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener("notificationclick", function (event) {
    event.notification.close();

    event.waitUntil(
        clients.matchAll({ type: "window", includeUncontrolled: true }).then(function (clientList) {
            for (const client of clientList) {
                if (client.url === event.notification.data.url && "focus" in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(event.notification.data.url);
            }
        })
    );
});
