/**
 * TWF NEWS - AI News Automation Bot Frontend Application
 */

document.addEventListener('DOMContentLoaded', () => {
  let selectedTopic = 'Artificial Intelligence';

  // DOM Elements
  const btnRunCrew = document.getElementById('btn-run-crew');
  const newsContainer = document.getElementById('news-container');
  const consoleOutput = document.getElementById('console-output');
  const tickerContent = document.getElementById('ticker-content');
  const lastUpdatedTag = document.getElementById('last-updated-tag');
  
  // Status Elements
  const statusSlack = document.getElementById('status-slack');
  const statusSheets = document.getElementById('status-sheets');
  const statusLlm = document.getElementById('status-llm');
  const statusNews = document.getElementById('status-news');

  // Modal Elements
  const btnOpenGuides = document.getElementById('btn-open-guides');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const guidesModal = document.getElementById('guides-modal');
  const modalTabs = document.querySelectorAll('.modal-tab');
  const tabPanes = document.querySelectorAll('.tab-pane');

  // 1. Topic Pill Handlers
  const topicPills = document.querySelectorAll('.topic-pill');
  topicPills.forEach(pill => {
    pill.addEventListener('click', () => {
      topicPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      selectedTopic = pill.getAttribute('data-topic');
      logToConsole(`[USER] Selected topic category: '${selectedTopic}'`);
      fetchLatestNews(selectedTopic);
    });
  });

  // 2. Fetch System Status (Runs parallel to page load)
  async function checkSystemStatus() {
    try {
      const res = await fetch('/api/status');
      if (res.ok) {
        const data = await res.json();
        
        // Update Integration badges
        statusSlack.textContent = data.integrations.slack_bot ? 'Active (xoxb Token)' : 'Simulated (Set Env)';
        statusSlack.className = `integ-status-text ${data.integrations.slack_bot ? 'active' : 'simulated'}`;

        statusSheets.textContent = data.integrations.google_sheets ? 'Active (GSpread)' : 'Simulated (Set Env)';
        statusSheets.className = `integ-status-text ${data.integrations.google_sheets ? 'active' : 'simulated'}`;

        statusLlm.textContent = data.integrations.groq_api ? 'Groq Llama-3.3' : (data.integrations.openai_api ? 'OpenAI GPT-4o' : 'Rule Fallback');
        statusLlm.className = `integ-status-text ${data.integrations.groq_api || data.integrations.openai_api ? 'active' : 'simulated'}`;

        statusNews.textContent = data.integrations.serper_api ? 'Serper.dev API' : 'Google News RSS';
        statusNews.className = 'integ-status-text active';
        return;
      }
    } catch (e) {
      console.warn('Status check notice:', e);
    }
    // Fallback status text if API loading
    statusSlack.textContent = 'Simulated (Set Env)';
    statusSheets.textContent = 'Simulated (Set Env)';
    statusLlm.textContent = 'Rule Fallback';
  }

  // 3. Fetch Latest News Data
  async function fetchLatestNews(topic = selectedTopic) {
    try {
      const res = await fetch(`/api/news?topic=${encodeURIComponent(topic)}`);
      if (res.ok) {
        const data = await res.json();
        renderNewsArticles(data.articles || []);
        if (data.execution_logs && data.execution_logs.length > 0) {
          data.execution_logs.forEach(log => logToConsole(log));
        }
      }
    } catch (e) {
      logToConsole(`[ERR] Failed to load news feed: ${e.message}`, 'error');
    }
  }

  // 4. Trigger News Crew Manual Execution
  async function triggerNewsCrew() {
    btnRunCrew.disabled = true;
    btnRunCrew.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Crew Active...`;
    
    logToConsole(`[CREW] Initiating Multi-Agent Crew for '${selectedTopic}'...`, 'info');
    
    renderLoadingSkeleton();

    try {
      const res = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: selectedTopic, max_articles: 5 })
      });

      if (res.ok) {
        const data = await res.json();
        
        // Print execution logs to console
        if (data.execution_logs) {
          data.execution_logs.forEach(log => logToConsole(log));
        }

        renderNewsArticles(data.articles || []);

        if (data.timestamp) {
          const timeStr = new Date(data.timestamp).toLocaleTimeString();
          lastUpdatedTag.textContent = `Updated: ${timeStr}`;
        }

        logToConsole(`[SYS] ✅ Multi-Agent Run completed successfully!`, 'ready');
      } else {
        logToConsole(`[ERR] Server returned error ${res.status}`, 'error');
      }
    } catch (e) {
      logToConsole(`[ERR] Execution failed: ${e.message}`, 'error');
    } finally {
      btnRunCrew.disabled = false;
      btnRunCrew.innerHTML = `<span class="btn-sheen"></span><i class="fa-solid fa-bolt"></i> Run AI News Crew Now`;
      checkSystemStatus();
    }
  }

  // 5. Render News Cards & Update BBC Ticker Marquee
  function renderNewsArticles(articles) {
    if (!articles || articles.length === 0) {
      newsContainer.innerHTML = `<div class="news-card-item"><p>No articles available yet. Click 'Run AI News Crew Now' above.</p></div>`;
      return;
    }

    newsContainer.innerHTML = '';
    const tickerItems = [];

    articles.forEach(item => {
      const card = document.createElement('div');
      card.className = 'news-card-item';

      const headline = item.headline || 'Untitled Story';
      const summary = item.summary || 'Summary unavailable.';
      const link = item.link || '#';
      const source = item.source || 'Google News';
      const date = item.date || 'Recent';

      tickerItems.push(`🌐 ${headline} (${source})`);

      card.innerHTML = `
        <div class="news-card-header">
          <h4 class="news-card-title">${escapeHtml(headline)}</h4>
        </div>
        <div class="news-card-summary">${escapeHtml(summary)}</div>
        <div class="news-card-footer">
          <span class="source-tag"><i class="fa-solid fa-signal"></i> ${escapeHtml(source)} • ${escapeHtml(date)}</span>
          <a href="${escapeHtml(link)}" target="_blank" rel="noopener" class="story-link">
            Read Full Story <i class="fa-solid fa-arrow-up-right-from-square"></i>
          </a>
        </div>
      `;

      newsContainer.appendChild(card);
    });

    // Update Bottom Marquee Ticker
    if (tickerItems.length > 0) {
      tickerContent.innerHTML = `<span>${tickerItems.join(' &nbsp;&nbsp;•&nbsp;&nbsp; ')}</span>`;
    }
  }

  function renderLoadingSkeleton() {
    newsContainer.innerHTML = `
      <div class="news-card-item">
        <div class="skeleton-line title"></div>
        <div class="skeleton-line text"></div>
        <div class="skeleton-line text short"></div>
      </div>
      <div class="news-card-item">
        <div class="skeleton-line title"></div>
        <div class="skeleton-line text"></div>
      </div>
    `;
  }

  function logToConsole(msg, type = 'info') {
    const line = document.createElement('div');
    line.className = `console-line ${type}`;
    line.textContent = msg;
    consoleOutput.appendChild(line);
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
  }

  function escapeHtml(str) {
    return str.replace(/[&<>"']/g, function(m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
  }

  // 6. Modal Controls
  btnOpenGuides.addEventListener('click', () => guidesModal.classList.remove('hidden'));
  btnCloseModal.addEventListener('click', () => guidesModal.classList.add('hidden'));

  modalTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      modalTabs.forEach(t => t.classList.remove('active'));
      tabPanes.forEach(p => p.classList.add('hidden'));
      
      tab.classList.add('active');
      const targetId = tab.getAttribute('data-tab');
      document.getElementById(targetId).classList.remove('hidden');
    });
  });

  // Event Listeners
  btnRunCrew.addEventListener('click', triggerNewsCrew);

  // Initialize immediately
  checkSystemStatus();
  fetchLatestNews();
});
