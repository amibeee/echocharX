document.addEventListener('DOMContentLoaded', function() {
    // Supplier negotiation
    const negotiationForm = document.getElementById('negotiationForm');
    if (negotiationForm) {
      negotiationForm.addEventListener('submit', function(e) {
        const initialPrice = parseFloat(document.getElementById('initialPrice').value);
        const targetPrice = parseFloat(document.getElementById('targetPrice').value);
        
        if (targetPrice >= initialPrice) {
          e.preventDefault();
          alert('Target price must be lower than initial price for negotiation!');
        }
      });
    }
    
    // Production management
    const productionForm = document.getElementById('productionForm');
    if (productionForm) {
      productionForm.addEventListener('submit', function(e) {
        const quantity = parseInt(document.getElementById('quantity').value);
        const rawMaterialUsed = parseFloat(document.getElementById('rawMaterialUsed').value);
        
        if (quantity <= 0 || rawMaterialUsed <= 0) {
          e.preventDefault();
          alert('Quantity and raw material used must be greater than zero!');
        }
      });
    }
    
    // Order status updates
    const orderStatusForm = document.getElementById('orderStatusForm');
    if (orderStatusForm) {
      const statusSelect = document.getElementById('status');
      const trackingNumberGroup = document.getElementById('trackingNumberGroup');
      
      statusSelect.addEventListener('change', function() {
        if (this.value === 'shipped') {
          trackingNumberGroup.style.display = 'block';
        } else {
          trackingNumberGroup.style.display = 'none';
        }
      });
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize datepickers
    const datepickers = document.querySelectorAll('.datepicker');
    datepickers.forEach(function(el) {
      new Datepicker(el, {
        format: 'yyyy-mm-dd',
        autohide: true
      });
    });
    
    // Alert auto-close
    const alertList = document.querySelectorAll('.alert:not(.alert-permanent)');
    alertList.forEach(function(alert) {
      const closeAlert = () => {
        alert.classList.add('fadeOut');
        setTimeout(() => {
          alert.remove();
        }, 500);
      };
      
      setTimeout(closeAlert, 5000);
    });
  });