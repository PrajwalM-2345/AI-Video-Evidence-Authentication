<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prajwal M — Systems Engineer</title>
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800;900&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
    
    <style>
        /* ===== RESET & BASE ===== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: #061A2F;
            color: #ffffff;
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            width: 100%;
            background: linear-gradient(180deg, #0A1A2F 0%, #061A2F 100%);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 194, 255, 0.1);
            border: 1px solid rgba(0, 194, 255, 0.1);
        }
        
        /* ===== SCROLLBAR ===== */
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #061A2F;
        }
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #0B4F8A, #00C2FF);
            border-radius: 10px;
        }
        
        /* ===== BANNER ===== */
        .banner {
            width: 100%;
            height: 120px;
            background: linear-gradient(90deg, #061A2F 0%, #0B4F8A 50%, #00C2FF 100%);
            border-radius: 16px;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
            animation: fadeIn 1.5s ease-in;
        }
        
        .banner::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2300C2FF' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
            opacity: 0.3;
        }
        
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(-20px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        
        /* ===== TYPOGRAPHY BANNER ===== */
        .typing-banner {
            text-align: center;
            margin: 20px 0;
        }
        
        .typing-banner h1 {
            font-size: 48px;
            font-weight: 800;
            background: linear-gradient(135deg, #00C2FF, #00E5FF, #00C2FF);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: shimmer 3s ease-in-out infinite;
            font-family: 'Inter', sans-serif;
            letter-spacing: -1px;
        }
        
        @keyframes shimmer {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .subtitle {
            text-align: center;
            font-size: 20px;
            font-weight: 600;
            color: #00C2FF;
            margin: 10px 0;
            letter-spacing: 0.5px;
        }
        
        .subtitle span {
            background: rgba(0, 194, 255, 0.1);
            padding: 4px 16px;
            border-radius: 20px;
            border: 1px solid rgba(0, 194, 255, 0.2);
            display: inline-block;
        }
        
        /* ===== TYPING SVG REPLACEMENT ===== */
        .typing-roles {
            text-align: center;
            margin: 25px 0;
            font-family: 'JetBrains Mono', monospace;
            font-size: 18px;
            font-weight: 700;
            color: #00C2FF;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 12px;
        }
        
        .typing-roles span {
            background: rgba(0, 194, 255, 0.08);
            padding: 8px 20px;
            border-radius: 30px;
            border: 1px solid rgba(0, 194, 255, 0.15);
            transition: all 0.3s ease;
            animation: pulseGlow 2s ease-in-out infinite;
        }
        
        .typing-roles span:hover {
            background: rgba(0, 194, 255, 0.2);
            transform: scale(1.05);
            box-shadow: 0 0 30px rgba(0, 194, 255, 0.2);
        }
        
        @keyframes pulseGlow {
            0%, 100% { box-shadow: 0 0 10px rgba(0, 194, 255, 0.1); }
            50% { box-shadow: 0 0 25px rgba(0, 194, 255, 0.3); }
        }
        
        /* ===== SOCIAL LINKS ===== */
        .social-links {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 25px 0 30px 0;
            flex-wrap: wrap;
        }
        
        .social-links a {
            display: inline-block;
            padding: 10px 28px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 14px;
            text-decoration: none;
            transition: all 0.3s ease;
            letter-spacing: 0.5px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #ffffff;
        }
        
        .social-links a:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(0, 194, 255, 0.3);
            border-color: #00C2FF;
        }
        
        .social-links a.github { background: #0D1117; border-color: #30363d; }
        .social-links a.linkedin { background: #0A66C2; border-color: #0A66C2; }
        .social-links a.leetcode { background: #FFA116; border-color: #FFA116; color: #000; }
        
        /* ===== SECTION TITLES ===== */
        .section-title {
            font-size: 28px;
            font-weight: 800;
            margin: 40px 0 20px 0;
            padding-bottom: 12px;
            border-bottom: 2px solid rgba(0, 194, 255, 0.2);
            position: relative;
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            width: 60px;
            height: 2px;
            background: linear-gradient(90deg, #00C2FF, transparent);
        }
        
        .section-title .emoji {
            margin-right: 10px;
        }
        
        /* ===== ABOUT ME ===== */
        .about-box {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid rgba(0, 194, 255, 0.08);
            margin-bottom: 10px;
        }
        
        .about-box blockquote {
            font-size: 18px;
            font-weight: 300;
            color: #a0c4e8;
            border-left: 3px solid #00C2FF;
            padding-left: 20px;
            margin: 15px 0;
            font-style: italic;
        }
        
        .about-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 20px;
        }
        
        .about-item {
            background: rgba(0, 194, 255, 0.05);
            padding: 15px 20px;
            border-radius: 12px;
            border-left: 3px solid #00C2FF;
        }
        
        .about-item strong {
            color: #00C2FF;
            display: block;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }
        
        .about-item p {
            color: #c0d8f0;
            font-size: 14px;
            line-height: 1.5;
        }
        
        /* ===== BADGE CONTAINERS ===== */
        .badge-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin: 15px 0;
        }
        
        .badge {
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.3px;
            transition: all 0.3s ease;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #ffffff;
        }
        
        .badge:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 194, 255, 0.2);
            border-color: #00C2FF;
        }
        
        .badge.primary { background: rgba(0, 194, 255, 0.15); border-color: rgba(0, 194, 255, 0.3); }
        .badge.dark { background: rgba(0, 0, 0, 0.3); }
        .badge.gold { background: rgba(255, 193, 7, 0.15); border-color: rgba(255, 193, 7, 0.3); color: #FFC107; }
        .badge.green { background: rgba(76, 175, 80, 0.15); border-color: rgba(76, 175, 80, 0.3); color: #81C784; }
        .badge.purple { background: rgba(156, 39, 176, 0.15); border-color: rgba(156, 39, 176, 0.3); color: #CE93D8; }
        
        /* ===== SKILL ICONS ===== */
        .skill-icons {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            justify-content: center;
            margin: 15px 0;
        }
        
        .skill-icon {
            background: rgba(255, 255, 255, 0.05);
            padding: 8px 16px;
            border-radius: 12px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            font-weight: 600;
            color: #a0c4e8;
            border: 1px solid rgba(255, 255, 255, 0.06);
            transition: all 0.3s ease;
        }
        
        .skill-icon:hover {
            background: rgba(0, 194, 255, 0.1);
            border-color: #00C2FF;
            transform: scale(1.05);
            color: #00C2FF;
        }
        
        /* ===== LINUX ECOSYSTEM ===== */
        .linux-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin: 15px 0;
        }
        
        .linux-card {
            background: rgba(255, 255, 255, 0.03);
            padding: 14px 18px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .linux-card:hover {
            background: rgba(0, 194, 255, 0.08);
            border-color: #00C2FF;
            transform: translateY(-3px);
        }
        
        .linux-card .distro {
            font-weight: 700;
            font-size: 14px;
            color: #ffffff;
        }
        
        .linux-card .version {
            font-size: 11px;
            color: #8899aa;
            margin-top: 4px;
        }
        
        /* ===== STATS ===== */
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(0, 194, 255, 0.08);
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            border-color: #00C2FF;
            box-shadow: 0 8px 30px rgba(0, 194, 255, 0.1);
        }
        
        .stat-card .number {
            font-size: 36px;
            font-weight: 800;
            background: linear-gradient(135deg, #00C2FF, #00E5FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-card .label {
            color: #8899aa;
            font-size: 13px;
            margin-top: 5px;
            font-weight: 500;
        }
        
        /* ===== BOTTOM BANNER ===== */
        .bottom-banner {
            width: 100%;
            height: 80px;
            background: linear-gradient(90deg, #00C2FF, #0B4F8A, #061A2F);
            border-radius: 16px;
            margin-top: 40px;
            opacity: 0.6;
            position: relative;
            overflow: hidden;
        }
        
        .bottom-banner::after {
            content: '✦ SYSTEMS ✦ AI ✦ INFRASTRUCTURE ✦';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: 800;
            font-size: 20px;
            letter-spacing: 8px;
            color: rgba(255, 255, 255, 0.3);
            white-space: nowrap;
            animation: scrollText 20s linear infinite;
        }
        
        @keyframes scrollText {
            0% { transform: translate(-50%, -50%) translateX(-50px); opacity: 0.3; }
            50% { opacity: 0.6; }
            100% { transform: translate(-50%, -50%) translateX(50px); opacity: 0.3; }
        }
        
        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {
            .container { padding: 20px; }
            .typing-banner h1 { font-size: 32px; }
            .subtitle { font-size: 16px; }
            .typing-roles { font-size: 14px; gap: 8px; }
            .typing-roles span { padding: 6px 14px; }
            .about-grid { grid-template-columns: 1fr; }
            .stats-grid { grid-template-columns: 1fr; }
            .linux-grid { grid-template-columns: 1fr 1fr; }
            .social-links a { padding: 8px 18px; font-size: 12px; }
            .badge { font-size: 10px; padding: 4px 12px; }
            .section-title { font-size: 22px; }
            .bottom-banner::after { font-size: 14px; letter-spacing: 4px; }
        }
        
        @media (max-width: 480px) {
            .linux-grid { grid-template-columns: 1fr; }
            .typing-banner h1 { font-size: 26px; }
            .container { padding: 15px; }
        }
    </style>
</head>
<body>

<div class="container">

    <!-- ===== BANNER ===== -->
    <div class="banner"></div>

    <!-- ===== TYPOGRAPHY BANNER ===== -->
    <div class="typing-banner">
        <h1>Hi 👋, I'm Prajwal M</h1>
    </div>

    <div class="subtitle">
        <span>Software Engineer | Systems Programming | Linux | AI Infrastructure</span>
    </div>

    <!-- ===== TYPING ROLES ===== -->
    <div class="typing-roles">
        <span>Systems Programming</span>
        <span>Linux Engineering</span>
        <span>Distributed Systems</span>
        <span>Cloud Infrastructure</span>
        <span>AI Infrastructure</span>
    </div>

    <!-- ===== SOCIAL LINKS ===== -->
    <div class="social-links">
        <a href="https://github.com/PrajwalM-2345" target="_blank" class="github">🐙 GitHub</a>
        <a href="https://www.linkedin.com/in/prajwal-m-74194928b/" target="_blank" class="linkedin">💼 LinkedIn</a>
        <a href="https://leetcode.com/u/Prajwal_M_77/" target="_blank" class="leetcode">⚡ LeetCode</a>
    </div>

    <!-- ===== ABOUT ME ===== -->
    <h2 class="section-title"><span class="emoji">👨🏻‍💻</span> About Me</h2>
    
    <div class="about-box">
        <blockquote>
            Systems-focused developer building robust architecture from kernel-level concepts up to scalable cloud and AI infrastructure.
        </blockquote>
        
        <div class="about-grid">
            <div class="about-item">
                <strong>🔭 Currently Focusing</strong>
                <p>Linux engineering, distributed systems, and AI platforms.</p>
            </div>
            <div class="about-item">
                <strong>🌱 Deep Diving Into</strong>
                <p>Database internals, compilers, and advanced memory management.</p>
            </div>
            <div class="about-item">
                <strong>💡 Philosophy</strong>
                <p>Clean architecture, blazing-fast tooling, and polished projects.</p>
            </div>
            <div class="about-item">
                <strong>⚡ Fun Fact</strong>
                <p>I love optimizing systems just as much as writing the code that runs on them.</p>
            </div>
        </div>
    </div>

    <!-- ===== CURRENT MISSION ===== -->
    <h2 class="section-title"><span class="emoji">🎯</span> Current Mission &amp; Focus</h2>
    
    <div class="badge-container">
        <span class="badge primary">DSA</span>
        <span class="badge primary">Problem Solving</span>
        <span class="badge primary">Operating Systems</span>
        <span class="badge primary">Distributed Systems</span>
        <span class="badge primary">AI Infrastructure</span>
    </div>

    <!-- ===== CORE STACK ===== -->
    <h2 class="section-title"><span class="emoji">⚙️</span> Core Stack &amp; Tools</h2>
    
    <div class="skill-icons">
        <span class="skill-icon">Linux</span>
        <span class="skill-icon">Bash</span>
        <span class="skill-icon">C</span>
        <span class="skill-icon">C#</span>
        <span class="skill-icon">C++</span>
        <span class="skill-icon">Java</span>
        <span class="skill-icon">Python</span>
        <span class="skill-icon">PowerShell</span>
        <span class="skill-icon">Git</span>
        <span class="skill-icon">GitHub</span>
        <span class="skill-icon">JavaScript</span>
        <span class="skill-icon">Node.js</span>
        <span class="skill-icon">React</span>
        <span class="skill-icon">HTML</span>
        <span class="skill-icon">CSS</span>
        <span class="skill-icon">Docker</span>
        <span class="skill-icon">GCP</span>
        <span class="skill-icon">AWS</span>
        <span class="skill-icon">Kubernetes</span>
        <span class="skill-icon">Terraform</span>
        <span class="skill-icon">Jenkins</span>
    </div>

    <div class="badge-container">
        <span class="badge gold">Computer Vision</span>
        <span class="badge gold">Blockchain</span>
        <span class="badge gold">Bitcoin</span>
        <span class="badge gold">MetaMask</span>
        <span class="badge gold">Cryptography</span>
    </div>

    <!-- ===== LINUX ECOSYSTEM ===== -->
    <h2 class="section-title"><span class="emoji">🐧</span> Linux Ecosystem &amp; Systems Engineering</h2>
    
    <h3 style="color: #00C2FF; font-size: 16px; margin: 15px 0 10px 0;">Daily Drivers</h3>
    <div class="badge-container" style="justify-content: flex-start;">
        <span class="badge green">Linux Mint Cinnamon</span>
        <span class="badge">macOS Sequoia</span>
        <span class="badge">Windows</span>
    </div>
    
    <h3 style="color: #00C2FF; font-size: 16px; margin: 15px 0 10px 0;">Distributions Explored</h3>
    <div class="linux-grid">
        <div class="linux-card"><div class="distro">Ubuntu</div><div class="version">Debian-based</div></div>
        <div class="linux-card"><div class="distro">Debian</div><div class="version">Stable</div></div>
        <div class="linux-card"><div class="distro">Arch Linux</div><div class="version">Rolling</div></div>
        <div class="linux-card"><div class="distro">Fedora</div><div class="version">RPM-based</div></div>
        <div class="linux-card"><div class="distro">Kali Linux</div><div class="version">Security</div></div>
        <div class="linux-card"><div class="distro">RHEL</div><div class="version">Enterprise</div></div>
        <div class="linux-card"><div class="distro">Peppermint</div><div class="version">Lightweight</div></div>
        <div class="linux-card"><div class="distro">Asahi Linux</div><div class="version">Apple Silicon</div></div>
        <div class="linux-card"><div class="distro">EndeavourOS</div><div class="version">Arch-based</div></div>
        <div class="linux-card"><div class="distro">Zorin OS</div><div class="version">Ubuntu-based</div></div>
    </div>
    
    <h3 style="color: #00C2FF; font-size: 16px; margin: 15px 0 10px 0;">Systems &amp; Low-Level Focus</h3>
    <div class="badge-container" style="justify-content: flex-start;">
        <span class="badge primary">Linux Kernel</span>
        <span class="badge primary">System Programming</span>
        <span class="badge primary">Socket Programming</span>
        <span class="badge primary">Pthreads</span>
        <span class="badge primary">IPC</span>
        <span class="badge purple">Memory Management</span>
        <span class="badge purple">Compiler Design</span>
        <span class="badge purple">Database Internals</span>
    </div>

    <!-- ===== GITHUB ANALYTICS ===== -->
    <h2 class="section-title"><span class="emoji">📊</span> GitHub Analytics</h2>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="number" id="repoCount">0</div>
            <div class="label">Public Repositories</div>
        </div>
        <div class="stat-card">
            <div class="number" id="commitCount">0</div>
            <div class="label">Total Commits</div>
        </div>
    </div>
    
    <!-- Stats placeholders (would be replaced with real data via API) -->
    <div style="display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; margin: 15px 0;">
        <div style="background: rgba(255,255,255,0.03); border-radius: 12px; padding: 15px 25px; border: 1px solid rgba(0,194,255,0.08); text-align: center; flex: 1; min-width: 200px;">
            <div style="font-size: 28px; font-weight: 800; color: #00C2FF;">⭐</div>
            <div style="font-size: 12px; color: #8899aa;">Stars Earned</div>
        </div>
        <div style="background: rgba(255,255,255,0.03); border-radius: 12px; padding: 15px 25px; border: 1px solid rgba(0,194,255,0.08); text-align: center; flex: 1; min-width: 200px;">
            <div style="font-size: 28px; font-weight: 800; color: #00C2FF;">🔀</div>
            <div style="font-size: 12px; color: #8899aa;">Forks</div>
        </div>
        <div style="background: rgba(255,255,255,0.03); border-radius: 12px; padding: 15px 25px; border: 1px solid rgba(0,194,255,0.08); text-align: center; flex: 1; min-width: 200px;">
            <div style="font-size: 28px; font-weight: 800; color: #00C2FF;">👥</div>
            <div style="font-size: 12px; color: #8899aa;">Followers</div>
        </div>
    </div>

    <!-- ===== BOTTOM BANNER ===== -->
    <div class="bottom-banner"></div>

    <!-- ===== FOOTER ===== -->
    <div style="text-align: center; margin-top: 25px; font-size: 12px; color: #445566; font-family: 'JetBrains Mono', monospace; letter-spacing: 2px;">
        ⚡ PRAJWAL M · SYSTEMS ENGINEER · 2026 ⚡
    </div>

</div>

<!-- ===== SCRIPT ===== -->
<script>
    // ============================================================
    // GitHub Stats Integration (Optional)
    // ============================================================
    // Uncomment below and replace 'PrajwalM-2345' with your username
    // to fetch real stats from GitHub API.
    // ============================================================
    
    /*
    async function fetchGitHubStats(username) {
        try {
            const response = await fetch(`https://api.github.com/users/${username}`);
            const data = await response.json();
            
            document.getElementById('repoCount').textContent = data.public_repos || 0;
            document.getElementById('commitCount').textContent = 'N/A';
            
            // For commit count, you'd need to fetch from events endpoint
            const eventsResponse = await fetch(`https://api.github.com/users/${username}/events/public`);
            const events = await eventsResponse.json();
            
            let totalCommits = 0;
            events.forEach(event => {
                if (event.type === 'PushEvent') {
                    totalCommits += event.payload.commits.length;
                }
            });
            
            document.getElementById('commitCount').textContent = totalCommits || 'N/A';
        } catch (error) {
            console.log('GitHub API not available — using placeholder stats.');
        }
    }
    
    // Call the function
    fetchGitHubStats('PrajwalM-2345');
    */
</script>

</body>
</html>
