document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views, () => is a callback function
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email); // dont need () =>, since we are not calling compose_email
  document.querySelector('#compose-form').addEventListener('submit', send_email); // ATTACH TO FORM, NOT BUTTON
  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-view').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
    .then(response => response.json())
    .then(emails => {
      // emails is a json array of objects
      // iterate over each email object and add it to view
      emails.forEach(email => {
        const emailElement = document.createElement('div');
        emailElement.classList.add('email');
        if (email.read) {
          emailElement.classList.add('read');
        } else {
          emailElement.classList.add('unread');
        }
        emailElement.innerHTML = `
          <strong>${email.sender}</a></strong>
          <p>${email.subject}</p>
          <p>${email.timestamp}</p>
        `; // use a click event instead of a new URL since app is single-page style
        // dont need to preventDefault since no <a> involved
        emailElement.addEventListener('click', () => {
          load_email(email.id, mailbox);
      });
        
        document.querySelector('#emails-view').appendChild(emailElement);
      });
    })
}

function load_email(email_id, mailbox) {

  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';

  fetch(`emails/${email_id}`)
    .then(response => response.json())
    .then(email => {
      // Show email details
      document.querySelector('#email-view').innerHTML = `
        <h3>${email.subject}</h3>
        <p>${email.timestamp}</p>
        <p><strong>From:</strong> ${email.sender}</p>
        <p><strong>To:</strong> ${email.recipients.join(', ')}</p>
        <hr>
        <div style="white-space: pre-wrap;">${email.body}</div>
      `; // white-space: pre-wrap preserves line breaks and spaces in body text, as HTML ignores \n

      // mark as read automatically after opening
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({ read: true })
      });

      // add an archive/unarchive button for mailboxes except sent
      if (mailbox !== "sent") {
        const archiveButton = document.createElement('button');
      
        if (email.archived) {
          archiveButton.innerHTML = 'Unarchive';
        } else {
          archiveButton.innerHTML = 'Archive';
        }
        archiveButton.addEventListener('click', () => {
          fetch(`/emails/${email_id}`, {
            method: 'PUT',
            body: JSON.stringify({ archived: !email.archived })
          }) // ! flips the value
          .then(() => { // no .json() here since views for PUT doesnt return JSON, so the rest of the code can run after promise finishes
            load_mailbox('inbox');
          });
        });
        document.querySelector('#email-view').appendChild(archiveButton);

        const replyButton = document.createElement('button');
        replyButton.innerHTML = 'Reply';
        replyButton.addEventListener('click', () => {

          document.querySelector('#emails-view').style.display = 'none';
          document.querySelector('#compose-view').style.display = 'block';
          document.querySelector('#email-view').style.display = 'none';

          // prefill

          document.querySelector('#compose-recipients').value = email.sender;
          // if subject already starts with Re:, dont add another Re:
          if (!email.subject.startsWith("Re: ")) {
            document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
          } else {
            document.querySelector('#compose-subject').value = email.subject;
          }
          const textarea = document.querySelector('#compose-body');

          // Pre-fill reply template
          textarea.value = `\n\nOn ${email.timestamp}, ${email.sender} wrote:\n${email.body}`;

          // Focus the textarea
          textarea.focus();

          // Move cursor to the very beginning (row 1, col 1) so users know where to type
          textarea.setSelectionRange(0, 0);

        })
        document.querySelector('#email-view').appendChild(replyButton);
      }
    });
  }

function send_email(event) {

  event.preventDefault(); // stop the form from reloading the page

  // Get the values from the compose fields
  const recipients = document.querySelector('#compose-recipients').value;
  const subject = document.querySelector('#compose-subject').value;
  const body = document.querySelector('#compose-body').value;

  // Send the email using a POST request (this is a placeholder, actual implementation may vary)
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients, // recipients are sent as a string, not an iterable of emails
      subject: subject,
      body: body
    })
  })
  .then(response => response.json()) // response would be the python dict passed into JsonResponse in compose() in views.py
  .then(result => {
    // Handle the result of sending the email
    if (result.error) {
        console.error(result.error); 
    } else {
        console.log(result.message);
    }
    load_mailbox('sent'); // Load sent mailbox after sending
  });
}