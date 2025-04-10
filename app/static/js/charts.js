// Utility to get CSS variable value
function getCSSVar(variable) {
    return getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
  }
  
  // ==============================
  // Dashboard Charts with Ambient Design
  // ==============================
  
  // Sales Chart
  function createSalesChart(data) {
    const ctx = document.getElementById('salesChart').getContext('2d');
  
    const dates = data.map(item => item.date);
    const amounts = data.map(item => item.amount);
  
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [
          {
            label: 'Sales Amount ($)',
            data: amounts,
            backgroundColor: 'rgba(93, 180, 90, 0.15)', // eco-green-light with transparency
            borderColor: getCSSVar('--eco-green'),
            borderWidth: 2,
            tension: 0.5,
            pointRadius: 4,
            pointBackgroundColor: getCSSVar('--eco-green-dark'),
            pointBorderColor: '#fff',
            fill: true
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: value => '$' + value
            },
            grid: {
              color: 'rgba(77, 52, 39, 0.05)'
            }
          },
          x: {
            grid: {
              color: 'rgba(77, 52, 39, 0.05)'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Monthly Sales',
            font: {
              size: 18
            },
            color: getCSSVar('--charcoal-dark')
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            titleColor: '#fff',
            bodyColor: '#eee',
            callbacks: {
              label: context => '$' + context.parsed.y
            }
          },
          legend: {
            labels: {
              color: getCSSVar('--charcoal-medium')
            }
          }
        }
      }
    });
  }
  
  // Inventory Chart
  function createInventoryChart(data) {
    const ctx = document.getElementById('inventoryChart').getContext('2d');
  
    const productNames = data.products.map(item => item.name);
    const stockLevels = data.products.map(item => item.stock);
  
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: productNames,
        datasets: [
          {
            label: 'Stock Level',
            data: stockLevels,
            backgroundColor: [
              'rgba(93, 180, 90, 0.6)',
              'rgba(58, 140, 58, 0.6)',
              'rgba(159, 123, 98, 0.6)',
              'rgba(77, 52, 39, 0.6)',
              'rgba(42, 109, 42, 0.6)'
            ],
            borderColor: getCSSVar('--charcoal-dark'),
            borderWidth: 1,
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: 'rgba(77, 52, 39, 0.05)'
            }
          },
          x: {
            grid: {
              color: 'rgba(77, 52, 39, 0.03)'
            }
          }
        },
        plugins: {
          title: {
            display: true,
            text: 'Current Inventory Levels',
            font: {
              size: 18
            },
            color: getCSSVar('--charcoal-dark')
          },
          legend: {
            labels: {
              color: getCSSVar('--charcoal-medium')
            }
          }
        }
      }
    });
  }
  
  // Production Chart
  function createProductionChart(data) {
    const ctx = document.getElementById('productionChart').getContext('2d');
  
    const productNames = data.map(item => item.product);
    const quantities = data.map(item => item.quantity);
  
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: productNames,
        datasets: [
          {
            data: quantities,
            backgroundColor: [
              'rgba(201, 152, 75, 0.8)',
              'rgba(233, 160, 59, 0.8)',
              'rgba(183, 120, 52, 0.8)',
              'rgba(77, 52, 39, 0.8)',
              'rgba(93, 180, 90, 0.8)'
            ],
            borderColor: getCSSVar('--eco-cream'),
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Production Distribution',
            font: {
              size: 18
            },
            color: getCSSVar('--charcoal-dark')
          },
          tooltip: {
            callbacks: {
              label: context => `${context.label}: ${context.parsed} units`
            }
          },
          legend: {
            labels: {
              color: getCSSVar('--charcoal-medium')
            }
          }
        }
      }
    });
  }
  
  // Raw Materials Chart
  function createRawMaterialsChart(data) {
    const ctx = document.getElementById('rawMaterialsChart').getContext('2d');
  
    const materialCounts = {
      date_kernel: 0,
      filter_component: 0
    };
  
    data.raw_materials.forEach(material => {
      materialCounts[material.type]++;
    });
  
    new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['Date Kernels', 'Filter Components'],
        datasets: [
          {
            data: [materialCounts.date_kernel, materialCounts.filter_component],
            backgroundColor: [
              'rgba(159, 123, 98, 0.7)',
              'rgba(93, 180, 90, 0.7)'
            ],
            borderColor: getCSSVar('--eco-cream'),
            borderWidth: 2
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          title: {
            display: true,
            text: 'Raw Materials Distribution',
            font: {
              size: 18
            },
            color: getCSSVar('--charcoal-dark')
          },
          legend: {
            labels: {
              color: getCSSVar('--charcoal-medium')
            }
          }
        }
      }
    });
  }
  
  // ==============================
  // Load Charts on Page Load
  // ==============================
  document.addEventListener('DOMContentLoaded', function () {
    const salesChartEl = document.getElementById('salesChart');
    const inventoryChartEl = document.getElementById('inventoryChart');
    const productionChartEl = document.getElementById('productionChart');
    const rawMaterialsChartEl = document.getElementById('rawMaterialsChart');
  
    if (salesChartEl) {
      fetch('/admin/api/chart/sales')
        .then(res => res.json())
        .then(data => createSalesChart(data))
        .catch(err => console.error('Error fetching sales data:', err));
    }
  
    if (inventoryChartEl && rawMaterialsChartEl) {
      fetch('/admin/api/chart/inventory')
        .then(res => res.json())
        .then(data => {
          createInventoryChart(data);
          createRawMaterialsChart(data);
        })
        .catch(err => console.error('Error fetching inventory data:', err));
    }
  
    if (productionChartEl) {
      fetch('/admin/api/chart/production')
        .then(res => res.json())
        .then(data => createProductionChart(data))
        .catch(err => console.error('Error fetching production data:', err));
    }
  });
  