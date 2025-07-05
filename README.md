# 🧠 IntelliDocs AI

**Chat with your PDF documents using AI!**

Transform your PDF documents into an intelligent assistant. Upload PDFs and ask questions about their content using Google's Gemini AI.

## 🚀 Quick Start (2 Simple Ways)

### **Method 1: Super Simple (Recommended)**
Since Streamlit is already working for you:

1. **Get Your API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key and copy it

2. **Set Up API Key**
   ```bash
   # Run the quick setup
   python quick_start.py
   ```
   - Follow the instructions to add your API key
   - Or manually edit the `.env` file

3. **Start the App**
   ```bash
   streamlit run app.py
   ```

### **Method 2: Windows Double-Click**
For Windows users - just double-click `start.bat` file!

### **Method 3: Full Setup (If needed)**
```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run setup script (handles folder paths with spaces)
python setup.py

# Add your API key to .env file
# Then run the app
streamlit run app.py
```

That's it! Open your browser and go to `http://localhost:8501`

## 📁 Simple Project Structure

```
intellidocs-ai/
├── app.py              # Main application (everything in one file)
├── requirements.txt    # Python dependencies
├── setup.py           # Setup script
├── .env               # Your API key and settings
└── README.md          # This file
```

## 🎯 How to Use

1. **Upload PDFs**: Click "Browse files" and select your PDF documents
2. **Process**: Click "⚡ Process Documents" and wait for completion
3. **Chat**: Type questions about your documents and get AI-powered answers
4. **Export**: Save your conversations as JSON or text files

## 💡 Example Questions

- "What are the main topics in these documents?"
- "Can you summarize the key findings?"
- "What recommendations are mentioned?"
- "Compare the different approaches discussed"

## ⚙️ Configuration

Edit the `.env` file to customize:

```env
# Required
GOOGLE_API_KEY=your_actual_api_key_here

# Optional settings
MODEL_NAME=gemini-2.0-flash-exp
TEMPERATURE=0.3
MAX_FILE_SIZE_MB=50
CHUNK_SIZE=10000
```

## 🎨 Features

- **Beautiful UI**: Modern interface with gradients and animations
- **Multi-Document Support**: Upload and analyze multiple PDFs at once
- **Source Citations**: See which documents and pages answers come from
- **Export Options**: Save conversations as JSON or text
- **Real-time Analytics**: Track document stats and processing metrics
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🔧 Troubleshooting

### Common Issues

**"'E:\Google' is not recognized" (Space in folder path)**
- This happens when your folder path has spaces
- ✅ **Solution**: Use `python quick_start.py` instead of `python setup.py`
- Or run `streamlit run app.py` directly if dependencies are installed

**"No module named 'streamlit'"**
```bash
pip install -r requirements.txt
```

**"Invalid API key"**
- Check your API key in the `.env` file
- Make sure you have API quota available
- Verify the key is active in Google AI Studio

**"No documents processed"**
- Make sure you're uploading PDF files (not images or other formats)
- Check file size is under 50MB
- Ensure PDFs contain readable text (not just images)

**"Port already in use"**
```bash
streamlit run app.py --server.port 8502
```

### Need Help?

1. **Check the logs**: Look for error messages in the terminal
2. **Run setup again**: `python setup.py`
3. **Check file permissions**: Make sure you have write access to the folder
4. **Update dependencies**: `pip install -r requirements.txt --upgrade`

## 🌟 Advanced Usage

### Custom Model Settings
Edit `.env` to change AI behavior:
- `TEMPERATURE=0.1` for more focused answers
- `TEMPERATURE=0.7` for more creative responses
- `CHUNK_SIZE=5000` for smaller documents
- `CHUNK_SIZE=15000` for larger documents

### Large Files
For documents over 50MB:
1. Edit `.env`: `MAX_FILE_SIZE_MB=100`
2. Restart the app
3. Consider splitting very large PDFs

### Multiple Sessions
Each browser tab creates a new session. You can:
- Process different documents in different tabs
- Compare responses across sessions
- Export conversations separately

## 🔐 Privacy & Security

- **Local Processing**: Documents are processed on your machine
- **API Calls**: Only text chunks are sent to Google AI (not full documents)
- **No Storage**: Google doesn't store your document content
- **Session Based**: Data is cleared when you close the browser

## 🚀 Performance Tips

- **Smaller chunks** = faster processing, less context
- **Larger chunks** = slower processing, better context
- **Fewer documents** = faster responses
- **More documents** = more comprehensive answers

## 📊 What's Happening Behind the Scenes

1. **PDF Text Extraction**: Extracts text from your PDFs
2. **Text Chunking**: Splits text into manageable pieces
3. **Vector Embedding**: Converts text to numerical representations
4. **Similarity Search**: Finds relevant chunks for your questions
5. **AI Response**: Generates answers using Google Gemini
6. **Source Attribution**: Links answers back to specific documents

## 🎁 Pro Tips

- **Be specific**: "What are the methodology limitations?" vs "Tell me about this"
- **Ask follow-ups**: Build on previous answers for deeper insights
- **Use document names**: "What does the 2023 report say about sales?"
- **Request structure**: "List the main points" or "Summarize in bullet points"

---

## 🛠️ Development

Want to modify the code? Here's the structure:

- **UI Components**: Search for `render_` functions
- **Document Processing**: Look for `process_documents` function
- **AI Chat**: Find `process_question` function
- **Styling**: Check the CSS in the `st.markdown` sections

## 📜 License

MIT License - feel free to use, modify, and distribute!

---

<div align="center">

**Made with ❤️ and AI**

Questions? Issues? Open a GitHub issue or contact support.

</div>