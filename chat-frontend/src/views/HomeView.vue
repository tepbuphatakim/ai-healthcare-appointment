<script setup></script>

<template>
  <div class="flex flex-col h-screen bg-gray-100">
    <!-- Header -->
    <header class="bg-white shadow-sm py-4 px-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <div class="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5 text-white"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path
                fill-rule="evenodd"
                d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
          <h1 class="text-lg font-semibold text-gray-800">AI Healthcare Appointment</h1>
        </div>
        <button class="text-gray-500 hover:text-gray-700">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
            />
          </svg>
        </button>
      </div>
    </header>

    <!-- Chat Messages -->
    <div class="flex-1 overflow-y-auto p-6 space-y-4" ref="chatContainer">
      <!-- Welcome Message -->
      <div class="flex items-start">
        <div class="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
          AI
        </div>
        <div class="ml-3 bg-white rounded-lg p-3 shadow max-w-md">
          <p class="text-gray-800">Welcome to Royal Phnom Penh Hospital! I'm your virtual assistant. I can help you find information about our doctors, their specialties, working hours, and how to schedule appointments. How may I assist you today?</p>
        </div>
      </div>

      <!-- Message Loop -->
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="{
          'flex items-start': message.sender === 'ai',
          'flex items-start justify-end': message.sender === 'user',
        }"
      >
        <!-- AI Message -->
        <template v-if="message.sender === 'ai'">
          <div class="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
            AI
          </div>
          <div class="ml-3 bg-white rounded-lg p-3 shadow max-w-md">
            <p class="text-gray-800" v-html="formatMessage(message.text)"></p>
          </div>
        </template>

        <!-- User Message -->
        <template v-else>
          <div class="mr-3 bg-blue-500 rounded-lg p-3 shadow max-w-md">
            <p class="text-white">{{ message.text }}</p>
          </div>
          <div class="h-8 w-8 rounded-full bg-gray-300 flex items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-5 w-5 text-gray-700"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fill-rule="evenodd"
                d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
                clip-rule="evenodd"
              />
            </svg>
          </div>
        </template>
      </div>

      <!-- Loading Indicator -->
      <div v-if="isLoading" class="flex items-start">
        <div class="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
          AI
        </div>
        <div class="ml-3 bg-white rounded-lg p-3 shadow">
          <div class="flex space-x-2">
            <div class="h-2 w-2 bg-gray-300 rounded-full animate-bounce"></div>
            <div
              class="h-2 w-2 bg-gray-300 rounded-full animate-bounce"
              style="animation-delay: 0.2s"
            ></div>
            <div
              class="h-2 w-2 bg-gray-300 rounded-full animate-bounce"
              style="animation-delay: 0.4s"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="bg-white border-t border-gray-200 p-4">
      <div class="flex items-center">
        <!-- <button class="text-gray-500 hover:text-gray-700 mr-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
          </svg>
        </button> -->
        <input
          type="text"
          v-model="userInput"
          @keyup.enter="sendMessage"
          placeholder="Type your message..."
          class="flex-1 border border-gray-300 rounded-full px-4 py-2 text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <button
          @click="sendMessage"
          class="ml-2 bg-blue-500 text-white rounded-full p-2 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HomeView',
  data() {
    return {
      userInput: '',
      messages: [],
      isLoading: false,
    }
  },
  methods: {
    async sendMessage() {
      if (!this.userInput.trim()) return

      // Add user message
      this.messages.push({
        sender: 'user',
        text: this.userInput,
      })

      const userQuestion = this.userInput
      this.userInput = ''

      // Show loading indicator
      this.isLoading = true
      const text = await this.generateResponse(userQuestion)
      this.isLoading = false

      this.messages.push({
        sender: 'ai',
        text,
      })
    },

    scrollToBottom() {
      const container = this.$refs.chatContainer
      container.scrollTop = container.scrollHeight
    },

    formatMessage(text) {
      // Handle markdown-like formatting
      // This is a simple implementation - consider using a proper markdown parser
      let formatted = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>')
        .replace(/\n/g, '<br>')

      return formatted
    },

    async generateResponse(question) {
      try {
        const response = await axios.post('http://localhost:5000/api/query', {
          question: question,
        })
        return response.data.answer
      } catch (error) {
        console.error('Error querying RAG system:', error)
        return 'Sorry, I encountered an error processing your question. Please try again.'
      }
    },
  },
  mounted() {
    // Scroll to bottom when component mounts
    this.scrollToBottom()
  },
}
</script>
