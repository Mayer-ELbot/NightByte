# Contributing to NightByte AI 🚀

Thank you for your interest in contributing to **NightByte AI**! We welcome contributions from developers, designers, translators, and gamers of all skill levels.

---

## 🛠️ How to Contribute

### 1. Reporting Bugs
- Check the [GitHub Issues](https://github.com/Mayer-ELbot/NightByte/issues) tab to see if the bug has already been reported.
- If not, open a new issue with:
  - A clear title and description.
  - Steps to reproduce the problem.
  - Your Windows version and launcher version.
  - Any relevant log messages from the **Event Log** tab.

### 2. Suggesting Enhancements
- Have an idea for a cool new platform detector, UI feature, or smart rule? Open an enhancement proposal in GitHub Issues!

### 3. Submitting Code Changes
1. **Fork** the repository.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/NightByte.git
   cd NightByte
   ```
3. Create a descriptive feature branch:
   ```bash
   git checkout -b feature/awesome-new-detector
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Make your improvements and test them thoroughly.
6. Commit with clear commit messages:
   ```bash
   git commit -m "Add detector for new game launcher XYZ"
   ```
7. Push to your branch and open a **Pull Request**!

---

## 🎨 Code Style Guidelines
- Follow PEP 8 guidelines for Python code.
- Keep the UI clean, minimalist, and accessible (WCAG AA contrast).
- All user-facing strings must be added to both `'ar'` and `'en'` dictionaries in `src/i18n/translations.py`.

---

## 📄 License
By contributing to NightByte AI, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
