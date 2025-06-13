import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://18.184.65.167:8003';

// Helper function für bessere Error-Responses
function createErrorResponse(error: unknown, backendUrl: string, method: string) {
  console.error(`Proxy ${method} error:`, error);
  const errorMessage = error instanceof Error ? error.message : 'Unknown error';
  
  // Detaillierte Fehlermeldung für besseres Debugging
  return NextResponse.json(
    { 
      error: 'Backend request failed',
      details: {
        message: errorMessage,
        backend_url: backendUrl,
        method: method,
        hint: 'Backend läuft möglicherweise nicht auf 18.184.65.167:8003. Prüfen Sie: curl http://18.184.65.167:8003/',
        timestamp: new Date().toISOString()
      }
    },
    { status: 503 } // 503 Service Unavailable ist passender
  );
}

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const path = url.searchParams.get('path') || '';
  const query = url.searchParams.get('query') || '';
  
  const backendUrl = `${BACKEND_URL}${path}${query ? `?${query}` : ''}`;
  
  try {
    const response = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return createErrorResponse(error, backendUrl, 'GET');
  }
}

export async function POST(request: NextRequest) {
  const url = new URL(request.url);
  const path = url.searchParams.get('path') || '';
  
  const backendUrl = `${BACKEND_URL}${path}`;
  
  try {
    const body = await request.json();
    const userIdHeader = request.headers.get('x-user-id');
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (userIdHeader) {
      headers['x-user-id'] = userIdHeader;
    }
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return createErrorResponse(error, backendUrl, 'POST');
  }
}

export async function PUT(request: NextRequest) {
  const url = new URL(request.url);
  const path = url.searchParams.get('path') || '';
  
  const backendUrl = `${BACKEND_URL}${path}`;
  
  try {
    const body = await request.json();
    const userIdHeader = request.headers.get('x-user-id');
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (userIdHeader) {
      headers['x-user-id'] = userIdHeader;
    }
    
    const response = await fetch(backendUrl, {
      method: 'PUT',
      headers,
      body: JSON.stringify(body),
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return createErrorResponse(error, backendUrl, 'PUT');
  }
}

export async function DELETE(request: NextRequest) {
  const url = new URL(request.url);
  const path = url.searchParams.get('path') || '';
  
  const backendUrl = `${BACKEND_URL}${path}`;
  
  try {
    const userIdHeader = request.headers.get('x-user-id');
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (userIdHeader) {
      headers['x-user-id'] = userIdHeader;
    }
    
    const response = await fetch(backendUrl, {
      method: 'DELETE',
      headers,
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return createErrorResponse(error, backendUrl, 'DELETE');
  }
} 