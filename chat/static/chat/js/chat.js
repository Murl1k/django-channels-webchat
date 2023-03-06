const userID = document.querySelector('#logged-in-user').value
let activeInterlocutor;

// Создание адреса вебскета
let loc = window.location
let wsStart = 'ws://'
if(loc.protocol === 'https') {wsStart = 'wss://'}
let endpoint = wsStart + loc.host + loc.pathname

const socket = new WebSocket(endpoint)

socket.onopen = async function(e){
    console.log(e)

    // При запуске получаем все чаты пользователя
    socket.send(JSON.stringify({
        'command': 'get_threads'
    }))
}

socket.onmessage = async function(e){
    const data = JSON.parse(e.data);
    console.log(data)

    // Получение команды и выполнение ее
    switch(data.command) {
        case 'get_threads':
            displayUsers(data.threads)
            break;
        case 'join':
            openChat(data.messages, data.user_info)
            break;
        case 'message':
            createMessage(data.message, data.author, data.author_avatar)
            break;
        case 'search':
            displayUsers(data.result)
            break;
    }
}

socket.onclose = async function(e){
    console.log('Socket closed', e)
}

// Ивент на поиск собеседника
document.querySelector('.interlocutors-search').onkeyup = function(e) {
    let searchValue = document.querySelector('.interlocutors-search').value
    let cmd;

    // Если задан пустой запрос, то получаем все чаты пользователя, иначе просто делаем поиск по пользователям.
    if (searchValue == '') {cmd = 'get_threads'} else {cmd = 'search'}

    socket.send(JSON.stringify(
        {
            'command': cmd,
            'value': searchValue
        }
    ))
}

// Вывод пользователей. users - список пользователей от бэкэнда со словарями (id, username, user_avatar)
function displayUsers(users) {
    let interlocutorsBody = document.querySelector('.interlocutors-items')
    interlocutorsBody.innerHTML = ''

    // Проходимся по всему списку пользователей и выводим каждого в сайдбар
    for (let i = 0; i < users.length; i++) {
        let user = users[i]
        let active = '';

        if (document.querySelector('.username')) {
            if (document.querySelector('.username').innerHTML.trim() === user.username) {
                active='active'
            }
        }

        interlocutorsBody.innerHTML += `
        <div class="single-interlocutor ${active}" interlocutor="${user.id}">
            <div class="interlocutor-avatar">
                <img src="${user.user_avatar}">
            </div>
            <span class="interlocutor-name">
                ${user.username}
            </span>
        </div>
        `
    }

    // На элемент каждого собеседника ставим ивент на открытие чата.
    document.querySelectorAll('.single-interlocutor').forEach(
        interlocutor => {
            interlocutor.onclick = function() {
                if (activeInterlocutor === interlocutor) {return} 
                if (activeInterlocutor && document.querySelector('.active')) {document.querySelector('.active').classList.remove('active')}
                interlocutor.classList.add('active')
                activeInterlocutor = interlocutor

                // Запрос получения сообщений чата с бэкэнда
                getMessages(interlocutor)
                
            }
        });
}

// Выводит сообщение при его создании. message - содержание сообщения, authorID - айди автора, author_avatar - ссылка на аватар автора
function createMessage(message, authorID, author_avatar){
    if (message.trim() === '') {
        return false;
    }

    let messageElement;
    let messageType;
    let date = new Date()
    let messagesBody = document.querySelector('.messages');


    if (authorID == userID) {messageType = 'sent'} else {messageType = 'recieved'}

    messageElement = `<div class="message ${messageType}">
                        <img class="message-avatar" src="${author_avatar}">
                        <span class="message-text">${message}
                            <span class="message-time" title="${date}">${date.getHours()}:${String(date.getMinutes()).padStart(2, "0")}</span>
                        </span>
                      </div>
    `

    messagesBody.insertAdjacentHTML('afterbegin', messageElement)
}

// Открывает чат. В аргументе указываются список сообщений, полченных в JSON от бэкэнда; информация о пользователе списком (username, avatar, status)
function openChat(messages, userInfo) {
    let mainBody = document.querySelector('.main-body')
    let chatMessages = getMessagesHTMLForm(messages)
    let otherUser = userInfo.username
    let otherUserStatus = userInfo.status
    let interlocutorAvatar = userInfo.avatar

    mainBody.innerHTML = `
    <div class="body-upper">
        <img class="user-avatar" src="${interlocutorAvatar}">
        <div class="user-info">
        <span class='username'>${otherUser}</span><br>
        <span class='user-status'>${otherUserStatus}</span>
        </div>
    </div>
    <div class="messages-box">
        <div class="messages">
            ${chatMessages}
        </div>
    </div>
    <div class="send-message-form" id='input-message'>
        <div class="text-area"><textarea id="message-text" type="text" placeholder="Написать сообщение..." maxlength="2048"></textarea></div>
        <div class="send-message"><i class="bi bi-send-fill"></i></div>
    </div>
    `

    let messageInput = document.querySelector('#message-text')
    let sendForm = document.querySelector('.send-message')

    // Ивент на отправку сообщения
    messageInput.onkeyup = function(e){
        if (e.shiftKey) {return false}
        if (e.keyCode === 13) {document.querySelector('.send-message').click()} 
    };

    // Отправление сообщения на сохранение в бд
    sendForm.onclick = function(e) {
        let messageValue = document.querySelector('#message-text').value;
        if (messageValue.trim() != '') {
            socket.send(JSON.stringify({
                'command': 'send_message',
                'interlocutor': getInterlocutorID(activeInterlocutor),
                'message': messageValue
            }))
        }
        document.querySelector('#message-text').value = '';
    }
}

 /* Конвертирует список сообщений в HTML элемент. В аргументе принимает список со словарями: 
    ('user': {'id': message_object.user.pk,
                'user_avatar': message_object.user.profile.avatar.url,
                'username': message_object.user.username
                },
    'message': message_object.message,
    'timestamp': str(message_object.timestamp))
*/
function getMessagesHTMLForm(messagesList) {
    let messagesElement = '';

    for (let i = 0; i < messagesList.length; i++) {
        let mes = messagesList[i]
        let mesType;
        let date = new Date(Date.parse(mes.timestamp))

        if (mes.user.id == userID) {mesType = 'sent'} else {mesType = 'recieved'}

        let mesElement = `
        <div class="message ${mesType}">
            <img title="${mes.user.username}" class="message-avatar" src="${mes.user.user_avatar}">
            <span class="message-text">${mes.message}
                <span class="message-time" title="${mes.timestamp}">${date.getHours()}:${String(date.getMinutes()).padStart(2, "0")}</span>
            </span>
        </div>
        `
        
        messagesElement += mesElement
    }

    return messagesElement
}

// Отправляет запрос на получение сообщений указанного Thread(чата).
function getMessages(interlocutor_) {
    socket.send(JSON.stringify(
        {  
            'command': 'join',
            'interlocutor': getInterlocutorID(interlocutor_)
        }
    ))
}

// Получение ID указанного собеседника. (Принимает HTML объект)
function getInterlocutorID(interlocutor_) {
    return interlocutor_.getAttribute('interlocutor')
}
