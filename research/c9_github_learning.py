#!/usr/bin/env python3
"""
C9 GitHub Repository Learning Module
Learns from user's tracked repositories to enhance capabilities.
Tracks: anthropic/claude-code, thewaltero/mythos-router, kyegomez/OpenMythos,
        cran/multiCA, multica-ai/multica, topic: claude-mythos
"""

import os
import json
import time
import requests
from datetime import datetime
from collections import deque
from pathlib import Path

class GitHubLearningEngine:
    """
    Learns from GitHub repositories to:
    - Extract code patterns and architectures
    - Track PRs and issues for new capabilities
    - Clone and analyze repo structures
    - Feed insights into C9 Assembly Index
    """

    TRACKED_REPOS = [
        "anthropic/claude-code",
        "thewaltero/mythos-router", 
        "kyegomez/OpenMythos",
        "cran/multiCA",
        "multica-ai/multica",
    ]

    TRACKED_TOPICS = ["claude-mythos"]

    def __init__(self, brain=None, c9=None):
        self.brain = brain
        self.c9 = c9
        self.knowledge_base = {}
        self.pr_cache = deque(maxlen=500)
        self.commit_cache = deque(maxlen=1000)
        self.learning_log = deque(maxlen=200)

        self.data_dir = Path.home() / "cloud9" / "github_learning"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self._load_knowledge()

    def _load_knowledge(self):
        """Load previously learned knowledge."""
        kb_path = self.data_dir / "knowledge_base.json"
        if kb_path.exists():
            with open(kb_path) as f:
                self.knowledge_base = json.load(f)
            print(f"[GH-LEARN] Loaded {len(self.knowledge_base)} knowledge entries")

    def _save_knowledge(self):
        """Persist learned knowledge."""
        kb_path = self.data_dir / "knowledge_base.json"
        with open(kb_path, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)

    def fetch_repo_info(self, repo: str) -> dict:
        """Fetch repository metadata from GitHub API."""
        url = f"https://api.github.com/repos/{repo}"
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"[GH-LEARN] â ï¸ {repo}: HTTP {resp.status_code}")
                return {}
        except Exception as e:
            print(f"[GH-LEARN] â {repo}: {e}")
            return {}

    def fetch_recent_prs(self, repo: str, state: str = "all", per_page: int = 10) -> list:
        """Fetch recent pull requests."""
        url = f"https://api.github.com/repos/{repo}/pulls?state={state}&per_page={per_page}&sort=updated"
        try:
            resp = requests.get(url, timeout=15)
            return resp.json() if resp.status_code == 200 else []
        except Exception as e:
            print(f"[GH-LEARN] â PR fetch failed for {repo}: {e}")
            return []

    def fetch_recent_commits(self, repo: str, per_page: int = 20) -> list:
        """Fetch recent commits."""
        url = f"https://api.github.com/repos/{repo}/commits?per_page={per_page}"
        try:
            resp = requests.get(url, timeout=15)
            return resp.json() if resp.status_code == 200 else []
        except Exception as e:
            print(f"[GH-LEARN] â Commit fetch failed for {repo}: {e}")
            return []

    def analyze_pr(self, pr: dict) -> dict:
        """Analyze a PR for learning."""
        return {
            "number": pr.get("number"),
            "title": pr.get("title", ""),
            "body": pr.get("body", "")[:1000],
            "state": pr.get("state"),
            "author": pr.get("user", {}).get("login", "unknown"),
            "created_at": pr.get("created_at"),
            "merged": pr.get("merged_at") is not None,
            "additions": pr.get("additions", 0),
            "deletions": pr.get("deletions", 0),
            "changed_files": pr.get("changed_files", 0),
        }

    def learn_from_repo(self, repo: str) -> dict:
        """Full learning cycle for a repository."""
        print(f"\n[GH-LEARN] ð Learning from {repo}...")

        info = self.fetch_repo_info(repo)
        if not info:
            return {"error": "Failed to fetch repo info"}

        # Store repo metadata
        self.knowledge_base[repo] = {
            "name": info.get("full_name"),
            "description": info.get("description", ""),
            "stars": info.get("stargazers_count", 0),
            "forks": info.get("forks_count", 0),
            "language": info.get("language", "unknown"),
            "topics": info.get("topics", []),
            "last_updated": info.get("updated_at"),
            "learned_at": datetime.now().isoformat(),
        }

        # Fetch and analyze PRs
        prs = self.fetch_recent_prs(repo)
        pr_insights = []
        for pr in prs:
            if isinstance(pr, dict):
                analyzed = self.analyze_pr(pr)
                pr_insights.append(analyzed)
                self.pr_cache.append({"repo": repo, "pr": analyzed})

        self.knowledge_base[repo]["recent_prs"] = pr_insights[:5]

        # Fetch commits
        commits = self.fetch_recent_commits(repo)
        commit_summaries = []
        for commit in commits[:10]:
            if isinstance(commit, dict):
                msg = commit.get("commit", {}).get("message", "")
                commit_summaries.append(msg[:200])

        self.knowledge_base[repo]["recent_commits"] = commit_summaries

        # AI-powered analysis
        if self.brain:
            analysis = self._ai_analyze_repo(repo, info, pr_insights, commit_summaries)
            self.knowledge_base[repo]["ai_analysis"] = analysis

        self._save_knowledge()

        print(f"   â Learned: {len(pr_insights)} PRs, {len(commit_summaries)} commits")

        return self.knowledge_base[repo]

    def _ai_analyze_repo(self, repo: str, info: dict, prs: list, commits: list) -> str:
        """Use AI to analyze repository patterns."""
        prompt = f"""Analyze this GitHub repository and identify:
1. Core architecture patterns
2. Key capabilities and features
3. Recent development trends from commits and PRs
4. How this could integrate with a sovereign AI system

REPO: {repo}
DESCRIPTION: {info.get('description', 'N/A')}
LANGUAGE: {info.get('language', 'N/A')}
TOPICS: {', '.join(info.get('topics', []))}

RECENT PRs:
"""
        for pr in prs[:5]:
            prompt += f"- #{pr['number']}: {pr['title']} ({pr['state']})\n"

        prompt += "\nRECENT COMMITS:\n"
        for commit in commits[:5]:
            prompt += f"- {commit[:100]}\n"

        try:
            result = self.brain.think(prompt, task_type="coding", prefer_backend="kimi", max_tokens=2000)
            return result["content"]
        except Exception as e:
            return f"AI analysis failed: {e}"

    def learn_all(self):
        """Learn from all tracked repositories."""
        print("[GH-LEARN] ð Starting full learning cycle...")
        for repo in self.TRACKED_REPOS:
            self.learn_from_repo(repo)
            time.sleep(2)  # Rate limit respect
        print(f"[GH-LEARN] â Learning complete. {len(self.knowledge_base)} repos in KB.")

    def search_topic(self, topic: str, per_page: int = 10) -> list:
        """Search GitHub for repositories by topic."""
        url = f"https://api.github.com/search/repositories?q=topic:{topic}&sort=updated&per_page={per_page}"
        try:
            resp = requests.get(url, timeout=15)
            data = resp.json()
            return data.get("items", [])
        except Exception as e:
            print(f"[GH-LEARN] â Topic search failed: {e}")
            return []

    def get_knowledge_summary(self) -> str:
        """Generate summary of learned knowledge."""
        summary = f"""ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
â  GITHUB LEARNING KNOWLEDGE BASE                              â
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

ð Repositories Learned: {len(self.knowledge_base)}
ð PRs Cached: {len(self.pr_cache)}
ð¾ Commits Cached: {len(self.commit_cache)}

"""
        for repo, data in self.knowledge_base.items():
            summary += f"\nð¦ {repo}\n"
            summary += f"   â­ {data.get('stars', 0)} | ð´ {data.get('forks', 0)} | ð¤ {data.get('language', '?')}\n"
            summary += f"   ð {data.get('description', 'No description')[:80]}\n"
            if data.get('ai_analysis'):
                summary += f"   ð¤ AI Analysis available\n"

        return summary


if __name__ == "__main__":
    engine = GitHubLearningEngine()
    engine.learn_all()
    print(engine.get_knowledge_summary())
