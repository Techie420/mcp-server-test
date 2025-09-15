import React, { useState } from 'react'
import Chatbot from './components/Chatbot.jsx'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="px-6 py-4 bg-white border-b">
        <h1 className="text-xl font-semibold">MCP Chatbot Dashboard</h1>
      </header>
      <main className="flex-1 p-4">
        <Chatbot />
      </main>
    </div>
  )
}


