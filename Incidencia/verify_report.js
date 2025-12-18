const fetch = require('node-fetch'); // Using native fetch if node 18+ or installing... wait, I shouldn't rely on packages not there.
// If node < 18, fetch might not be available.
// I'll use http module or try 'fetch' assuming newer node.
// Given the user context "The user's OS version is windows", and recent projects usually have node 18+.
// If 'fetch' is not defined, I'll fallback to http.

async function verify() {
  const url = 'http://localhost:3000/api/incidencias/reporte-sabana';
  const data = {
    fecha_inicio: '2024-01-01',
    fecha_fin: '2025-12-31'
  };

  console.log('Testing success case...');
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    console.log('Status:', response.status);
    console.log('Response:', JSON.stringify(result, null, 2));
    
    if (response.status === 200 && result.data) {
        console.log('SUCCESS: Endpoint works!');
    } else {
        console.log('FAILURE: Unexpected response');
    }

  } catch (error) {
    console.error('Error:', error);
  }

  console.log('\nTesting error case (missing dates)...');
  try {
     const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const result = await response.json();
    console.log('Status:', response.status);
    console.log('Response:', JSON.stringify(result, null, 2));

    if (response.status === 400) {
        console.log('SUCCESS: Error handling works!');
    } else {
        console.log('FAILURE: Should have returned 400');
    }

  } catch (err) {
      console.error(err);
  }
}

verify();
