document.addEventListener('DOMContentLoaded', function() {
    // Quantity controls for products
    const quantityControls = document.querySelectorAll('.quantity-control');
    
    quantityControls.forEach(control => {
      const decreaseBtn = control.querySelector('.decrease');
      const increaseBtn = control.querySelector('.increase');
      const quantityInput = control.querySelector('input[type="number"]');
      const stockLimit = parseInt(quantityInput.getAttribute('max'));
      
      decreaseBtn.addEventListener('click', () => {
        let value = parseInt(quantityInput.value);
        if (value > 1) {
          quantityInput.value = value - 1;
        }
      });
      
      increaseBtn.addEventListener('click', () => {
        let value = parseInt(quantityInput.value);
        if (value < stockLimit) {
          quantityInput.value = value + 1;
        }
      });
      
      quantityInput.addEventListener('change', () => {
        let value = parseInt(quantityInput.value);
        if (value < 1) {
          quantityInput.value = 1;
        } else if (value > stockLimit) {
          quantityInput.value = stockLimit;
        }
      });
    });
    
    // Cart item quantity update
    const cartUpdateForms = document.querySelectorAll('.cart-update-form');
    
    cartUpdateForms.forEach(form => {
      const quantityInput = form.querySelector('input[name="quantity"]');
      const initialValue = quantityInput.value;
      
      quantityInput.addEventListener('change', () => {
        if (quantityInput.value !== initialValue) {
          form.submit();
        }
      });
    });
    
    // Checkout form validation
    const checkoutForm = document.getElementById('checkoutForm');
    
    if (checkoutForm) {
      checkoutForm.addEventListener('submit', function(e) {
        const shippingAddress = document.getElementById('shippingAddress').value;
        
        if (!shippingAddress.trim()) {
          e.preventDefault();
          alert('Please provide a shipping address!');
        }
      });
    }
    
    // Product filter
    const filterBtns = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.product-card');
    
    if (filterBtns.length > 0) {
      filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
          // Remove active class from all buttons
          filterBtns.forEach(b => b.classList.remove('active'));
          
          // Add active class to clicked button
          btn.classList.add('active');
          
          const filter = btn.getAttribute('data-filter');
          
          productCards.forEach(card => {
            if (filter === 'all') {
              card.style.display = 'block';
            } else {
              const productType = card.getAttribute('data-type');
              if (productType === filter) {
                card.style.display = 'block';
              } else {
                card.style.display = 'none';
              }
            }
          });
        });
      });
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