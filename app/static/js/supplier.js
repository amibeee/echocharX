document.addEventListener('DOMContentLoaded', function() {
    // Supply form validation
    const supplyForm = document.getElementById('supplyForm');
    if (supplyForm) {
      supplyForm.addEventListener('submit', function(e) {
        const quantity = parseFloat(document.getElementById('quantity').value);
        const unitPrice = parseFloat(document.getElementById('unitPrice').value);
        
        if (quantity <= 0 || unitPrice <= 0) {
          e.preventDefault();
          alert('Quantity and unit price must be greater than zero!');
        }
      });
    }
    
    // Negotiation counter offer
    const counterOfferForm = document.getElementById('counterOfferForm');
    if (counterOfferForm) {
      const currentPriceEl = document.getElementById('currentPrice');
      const counterPriceEl = document.getElementById('counterPrice');
      
      counterPriceEl.addEventListener('input', function() {
        const currentPrice = parseFloat(currentPriceEl.value);
        const counterPrice = parseFloat(this.value);
        
        if (counterPrice < currentPrice) {
          this.setCustomValidity('Counter price must be higher than or equal to current price!');
        } else {
          this.setCustomValidity('');
        }
      });
    }
    
    // Auto calculate total price for supply
    const quantityInput = document.getElementById('quantity');
    const unitPriceInput = document.getElementById('unitPrice');
    const totalPriceDisplay = document.getElementById('totalPriceDisplay');
    
    if (quantityInput && unitPriceInput && totalPriceDisplay) {
      const calculateTotal = () => {
        const quantity = parseFloat(quantityInput.value) || 0;
        const unitPrice = parseFloat(unitPriceInput.value) || 0;
        const total = quantity * unitPrice;
        
        totalPriceDisplay.textContent = '$' + total.toFixed(2);
      };
      
      quantityInput.addEventListener('input', calculateTotal);
      unitPriceInput.addEventListener('input', calculateTotal);
      
      // Initial calculation
      calculateTotal();
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
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