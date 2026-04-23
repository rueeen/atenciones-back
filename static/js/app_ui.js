(function () {
  const initDataTables = () => {
    if (typeof window.DataTable === 'undefined') {
      return;
    }

    const tables = document.querySelectorAll('table.app-table');
    tables.forEach((table) => {
      if (table.dataset.datatableInitialized === 'true') {
        return;
      }

      const hasFooter = table.querySelectorAll('tfoot th, tfoot td').length > 0;
      const columnDefs = hasFooter
        ? []
        : [{ targets: '_all', orderSequence: ['asc', 'desc'] }];

      // eslint-disable-next-line no-new
      new window.DataTable(table, {
        responsive: true,
        autoWidth: false,
        pageLength: 10,
        order: [],
        language: {
          url: 'https://cdn.datatables.net/plug-ins/2.0.8/i18n/es-ES.json',
        },
        columnDefs,
      });

      table.dataset.datatableInitialized = 'true';
    });
  };

  const initNotyfMessages = () => {
    const messagesNode = document.getElementById('django-messages-data');
    if (!messagesNode || typeof window.Notyf === 'undefined') {
      return;
    }

    let messages = [];
    try {
      messages = JSON.parse(messagesNode.textContent || '[]');
    } catch (error) {
      return;
    }

    if (!Array.isArray(messages) || messages.length === 0) {
      return;
    }

    const notyf = new window.Notyf({
      duration: 4000,
      dismissible: true,
      position: { x: 'right', y: 'top' },
    });

    messages.forEach((message) => {
      const messageType = (message.tags || '').toLowerCase();
      const text = message.message || '';

      if (!text) {
        return;
      }

      if (messageType.includes('error')) {
        notyf.error(text);
      } else {
        notyf.success(text);
      }
    });
  };

  document.addEventListener('DOMContentLoaded', function () {
    initDataTables();
    initNotyfMessages();
  });
})();
