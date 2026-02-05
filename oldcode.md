# 旧代码存档
# 存档开始时间: 2026-02-05
# 原因: 念旧，保留旧实现

## normalizeUrl 函数的旧实现（版本1）

```javascript
function normalizeUrl(url) {
    try {
        // 处理完整的URL（包括http://和https://）
        if (url.startsWith('http://') || url.startsWith('https://')) {
            const parsedUrl = new URL(url);
            // 如果是外部链接（不是当前域名），直接返回原URL
            if (parsedUrl.hostname !== window.location.hostname) {
                return url;
            }
            // 如果是内部链接，返回pathname
            return parsedUrl.pathname;
        }
        
        // 处理绝对路径
        if (url.startsWith('/')) {
            return url;
        }
        
        // 处理相对路径
        const baseUrl = window.location.origin + window.location.pathname;
        const resolvedUrl = new URL(url, baseUrl);
        
        return resolvedUrl.pathname;
    } catch (error) {
        console.warn('URL规范化失败:', error, url);
        // 返回原始URL作为备选
        return url;
    }
}
```

## 说明
这个实现会智能处理外部链接和内部链接，确保外部链接保持原样，内部链接被规范化为相对路径。

---

## normalizeUrl 函数的旧实现（版本2 - 硬编码特定地址）

```javascript
function normalizeUrl(url) {
    try {
        // 硬编码处理特定地址：https://pyspos.us.ci/ota/ota/releases.html
        if (url.includes('pyspos.us.ci/ota/ota/releases.html')) {
            return '/ota/releases.html';
        }
        
        // 处理完整的URL（包括http://和https://）
        if (url.startsWith('http://') || url.startsWith('https://')) {
            const parsedUrl = new URL(url);
            // 如果是外部链接（不是当前域名），直接返回原URL
            if (parsedUrl.hostname !== window.location.hostname) {
                return url;
            }
            // 如果是内部链接，返回pathname
            return parsedUrl.pathname;
        }
        
        // 处理绝对路径
        if (url.startsWith('/')) {
            return url;
        }
        
        // 处理相对路径
        const baseUrl = window.location.origin + window.location.pathname;
        const resolvedUrl = new URL(url, baseUrl);
        
        return resolvedUrl.pathname;
    } catch (error) {
        console.warn('URL规范化失败:', error, url);
        // 返回原始URL作为备选
        return url;
    }
}
```

## 说明
这个版本添加了硬编码处理特定地址的功能，防止404错误。（但404错误依然存在，并没有实质性解决）

---

## normalizeUrl 函数的旧实现（版本3 - 硬编码所有内部链接）

```javascript
function normalizeUrl(url) {
    try {
        // 硬编码处理所有内部链接，防止404错误
        const hardcodedMappings = {
            // 主页相关
            'index.html': '/index.html',
            '/index.html': '/index.html',
            
            // OTA更新页面相关
            'ota/index.html': '/ota/index.html',
            '/ota/index.html': '/ota/index.html',
            
            // 版本历史页面相关
            'ota/releases.html': '/ota/releases.html',
            '/ota/releases.html': '/ota/releases.html',
            
            // 处理可能的重复路径
            'ota/ota/index.html': '/ota/index.html',
            'ota/ota/releases.html': '/ota/releases.html',
            
            // 完整URL处理
            'pyspos.us.ci/index.html': '/index.html',
            'pyspos.us.ci/ota/index.html': '/ota/index.html',
            'pyspos.us.ci/ota/releases.html': '/ota/releases.html',
            'pyspos.us.ci/ota/ota/index.html': '/ota/index.html',
            'pyspos.us.ci/ota/ota/releases.html': '/ota/releases.html',
            
            // HTTPS版本
            'https://pyspos.us.ci/index.html': '/index.html',
            'https://pyspos.us.ci/ota/index.html': '/ota/index.html',
            'https://pyspos.us.ci/ota/releases.html': '/ota/releases.html',
            'https://pyspos.us.ci/ota/ota/index.html': '/ota/index.html',
            'https://pyspos.us.ci/ota/ota/releases.html': '/ota/releases.html',
            
            // HTTP版本
            'http://pyspos.us.ci/index.html': '/index.html',
            'http://pyspos.us.ci/ota/index.html': '/ota/index.html',
            'http://pyspos.us.ci/ota/releases.html': '/ota/releases.html',
            'http://pyspos.us.ci/ota/ota/index.html': '/ota/index.html',
            'http://pyspos.us.ci/ota/ota/releases.html': '/ota/releases.html',
        };
        
        // 检查是否匹配硬编码映射
        for (const [key, value] of Object.entries(hardcodedMappings)) {
            if (url.includes(key)) {
                return value;
            }
        }
        
        // 处理完整的URL（包括http://和https://）
        if (url.startsWith('http://') || url.startsWith('https://')) {
            const parsedUrl = new URL(url);
            // 如果是外部链接（不是当前域名），直接返回原URL
            if (parsedUrl.hostname !== window.location.hostname) {
                return url;
            }
            // 如果是内部链接，返回pathname
            return parsedUrl.pathname;
        }
        
        // 处理绝对路径
        if (url.startsWith('/')) {
            return url;
        }
        
        // 处理相对路径
        const baseUrl = window.location.origin + window.location.pathname;
        const resolvedUrl = new URL(url, baseUrl);
        
        return resolvedUrl.pathname;
    } catch (error) {
        console.warn('URL规范化失败:', error, url);
        // 返回原始URL作为备选
        return url;
    }
}
```

## 说明
这个版本硬编码了所有内部链接，但存在一个问题：'index.html'映射有冲突，导致从OTA页面返回主页时无法正确导航。需要根据当前页面上下文来决定映射关系。

---

## normalizeUrl 函数的旧实现（版本4 - 智能硬编码，只处理重复路径）

```javascript
function normalizeUrl(url) {
    try {
        // 硬编码处理特定的问题URL，防止404错误
        const hardcodedMappings = {
            // 处理重复路径问题
            'ota/ota/index.html': '/ota/index.html',
            'ota/ota/releases.html': '/ota/releases.html',
            
            // 处理可能的多次重复
            'ota/ota/ota/index.html': '/ota/index.html',
            'ota/ota/ota/releases.html': '/ota/releases.html',
            
            // 处理完整URL中的重复路径
            'pyspos.us.ci/ota/ota/index.html': '/ota/index.html',
            'pyspos.us.ci/ota/ota/releases.html': '/ota/releases.html',
            
            // HTTPS版本
            'https://pyspos.us.ci/ota/ota/index.html': '/ota/index.html',
            'https://pyspos.us.ci/ota/ota/releases.html': '/ota/releases.html',
            
            // HTTP版本
            'http://pyspos.us.ci/ota/ota/index.html': '/ota/index.html',
            'http://pyspos.us.ci/ota/ota/releases.html': '/ota/releases.html',
            
            // 处理localhost的重复路径
            'localhost:8000/ota/ota/index.html': '/ota/index.html',
            'localhost:8000/ota/ota/releases.html': '/ota/releases.html',
            'localhost:8080/ota/ota/index.html': '/ota/index.html',
            'localhost:8080/ota/ota/releases.html': '/ota/releases.html',
        };
        
        // 检查是否匹配硬编码映射（只处理重复路径问题）
        for (const [key, value] of Object.entries(hardcodedMappings)) {
            if (url.includes(key)) {
                return value;
            }
        }
        
        // 处理完整的URL（包括http://和https://）
        if (url.startsWith('http://') || url.startsWith('https://')) {
            const parsedUrl = new URL(url);
            // 如果是外部链接（不是当前域名），直接返回原URL
            if (parsedUrl.hostname !== window.location.hostname) {
                return url;
            }
            // 如果是内部链接，返回pathname
            return parsedUrl.pathname;
        }
        
        // 处理绝对路径
        if (url.startsWith('/')) {
            return url;
        }
        
        // 处理相对路径
        const baseUrl = window.location.origin + window.location.pathname;
        const resolvedUrl = new URL(url, baseUrl);
        
        return resolvedUrl.pathname;
    } catch (error) {
        console.warn('URL规范化失败:', error, url);
        // 返回原始URL作为备选
        return url;
    }
}
```

## 说明
这个版本采用智能硬编码策略，只处理重复路径问题，不干扰正常的相对路径解析。这样既能防止404错误，又能保证SPA导航正常工作。

---

## executePageScripts 函数的旧实现（版本1 - 执行所有脚本）

```javascript
function executePageScripts(doc, url) {
    // 获取页面中的所有script标签
    const scripts = doc.querySelectorAll('script');
    
    scripts.forEach(oldScript => {
        if (oldScript.src) {
            // 外部脚本 - 创建新的script标签
            const newScript = document.createElement('script');
            newScript.src = oldScript.src;
            if (oldScript.type) newScript.type = oldScript.type;
            if (oldScript.async) newScript.async = oldScript.async;
            if (oldScript.defer) newScript.defer = oldScript.defer;
            document.head.appendChild(newScript);
        } else if (oldScript.textContent.trim()) {
            // 使用eval执行（注意安全）
            try {
                eval(oldScript.textContent);
            } catch (e) {
                console.warn('执行内联脚本时出错:', e);
            }
        }
    });
}
```

## 说明
这个实现会执行新页面中的所有脚本，包括导航相关的脚本，这会导致导航状态被重置，造成SPA导航失效。

---

## executePageScripts 函数的旧实现（版本2 - 跳过导航相关脚本）

```javascript
function executePageScripts(doc, url) {
    // 获取页面中的所有script标签
    const scripts = doc.querySelectorAll('script');
    
    scripts.forEach(oldScript => {
        // 跳过导航相关的脚本
        const scriptContent = oldScript.textContent;
        if (scriptContent && (
            scriptContent.includes('function loadPageContent') ||
            scriptContent.includes('function normalizeUrl') ||
            scriptContent.includes('function isSamePage') ||
            scriptContent.includes('function executePageScripts') ||
            scriptContent.includes('function initNavIndicator') ||
            scriptContent.includes('function updateNavIndicator') ||
            scriptContent.includes('function checkAndRedirectUrl') ||
            scriptContent.includes('function toggleMenu') ||
            scriptContent.includes('let isNavigating') ||
            scriptContent.includes('let currentFetchController') ||
            scriptContent.includes('let navigationQueue') ||
            scriptContent.includes('let isInitialized') ||
            scriptContent.includes('let resizeTimeout') ||
            scriptContent.includes('const navLinks') ||
            scriptContent.includes('const navMenu') ||
            scriptContent.includes('const navIndicator') ||
            scriptContent.includes('const navToggle') ||
            scriptContent.includes("addEventListener('click'") ||
            scriptContent.includes("addEventListener('popstate'") ||
            scriptContent.includes("addEventListener('resize'") ||
            scriptContent.includes('window.history.pushState') ||
            scriptContent.includes('window.history.replaceState')
        )) {
            return;
        }
        
        if (oldScript.src) {
            // 外部脚本 - 创建新的script标签
            const newScript = document.createElement('script');
            newScript.src = oldScript.src;
            if (oldScript.type) newScript.type = oldScript.type;
            if (oldScript.async) newScript.async = oldScript.async;
            if (oldScript.defer) newScript.defer = oldScript.defer;
            document.head.appendChild(newScript);
        } else if (oldScript.textContent.trim()) {
            // 使用eval执行（注意安全）
            try {
                eval(oldScript.textContent);
            } catch (e) {
                console.warn('执行内联脚本时出错:', e);
            }
        }
    });
}
```

## 说明
这个实现会跳过导航相关的脚本，只执行页面特定的业务逻辑脚本，确保SPA导航状态不会被重置。

---

## normalizeUrl 函数的旧实现（版本5 - 使用正则表达式精确处理重复路径）

```javascript
function normalizeUrl(url) {
    try {
        // 使用正则表达式精确处理重复路径问题
        const duplicatePathPatterns = [
            // 匹配 ota/ota/index.html 或 ota/ota/releases.html
            /\/ota\/ota\/(index|releases)\.html/,
            // 匹配多次重复的 ota 路径
            /\/ota(?:\/ota)+\/(index|releases)\.html/,
            // 匹配完整URL中的重复路径
            /https?:\/\/[^\/]+\/ota\/ota\/(index|releases)\.html/,
            // 匹配 localhost 的重复路径
            /localhost:\d+\/ota\/ota\/(index|releases)\.html/,
        ];
        
        // 检查是否匹配重复路径模式
        for (const pattern of duplicatePathPatterns) {
            const match = url.match(pattern);
            if (match) {
                // 提取文件名并返回正确的路径
                const filename = match[1];
                return `/ota/${filename}.html`;
            }
        }
        
        // 处理完整的URL（包括http://和https://）
        if (url.startsWith('http://') || url.startsWith('https://')) {
            const parsedUrl = new URL(url);
            // 如果是外部链接（不是当前域名），直接返回原URL
            if (parsedUrl.hostname !== window.location.hostname) {
                return url;
            }
            // 如果是内部链接，返回pathname
            return parsedUrl.pathname;
        }
        
        // 处理绝对路径
        if (url.startsWith('/')) {
            return url;
        }
        
        // 处理相对路径
        const baseUrl = window.location.origin + window.location.pathname;
        const resolvedUrl = new URL(url, baseUrl);
        
        return resolvedUrl.pathname;
    } catch (error) {
        console.warn('URL规范化失败:', error, url);
        // 返回原始URL作为备选
        return url;
    }
}
```

## 说明
这个版本使用正则表达式精确匹配重复路径模式，能够处理各种变体，包括多次重复、完整URL、localhost等。相比硬编码映射，正则表达式更灵活且易于维护。

---

## 页面初始化URL纠正（版本1 - 在DOMContentLoaded中添加URL检查）

```javascript
document.addEventListener('DOMContentLoaded', function() {
    // 检查并纠正当前URL中的重复路径
    const currentPath = window.location.pathname;
    const normalizedPath = normalizeUrl(currentPath);
    if (currentPath !== normalizedPath) {
        // 如果URL包含重复路径，立即纠正
        window.history.replaceState({}, '', normalizedPath);
    }
    
    // 其他初始化代码...
});
```

## 说明
这个修复在页面加载时立即检查并纠正URL中的重复路径，防止用户直接访问包含重复路径的URL时出现404错误。使用`window.history.replaceState`而不是`pushState`，避免创建不必要的历史记录条目。

---

## popstate事件处理修复（版本1 - 确保使用规范化后的URL）

```javascript
window.addEventListener('popstate', function() {
    // 当用户点击前进后退按钮时，重新加载当前页面内容
    // 使用规范化后的URL，避免路径重复叠加
    const currentPath = normalizeUrl(window.location.pathname);
    // 确保使用绝对路径进行fetch请求
    loadPageContent(currentPath);
});
```

## 说明
这个修复确保在用户点击浏览器前进后退按钮时，使用规范化后的URL进行页面加载，避免重复路径问题。

---

## normalizeUrl 函数的旧实现（版本6 - 处理缺少 ota/ 前缀的情况）

```javascript
function normalizeUrl(url) {
    try {
        // 使用正则表达式精确处理重复路径问题
        const duplicatePathPatterns = [
            // 匹配 ota/ota/index.html 或 ota/ota/releases.html
            /\/ota\/ota\/(index|releases)\.html/,
            // 匹配多次重复的 ota 路径
            /\/ota(?:\/ota)+\/(index|releases)\.html/,
            // 匹配完整URL中的重复路径
            /https?:\/\/[^\/]+\/ota\/ota\/(index|releases)\.html/,
            // 匹配 localhost 的重复路径
            /localhost:\d+\/ota\/ota\/(index|releases)\.html/,
        ];
        
        // 检查是否匹配重复路径模式
        for (const pattern of duplicatePathPatterns) {
            const match = url.match(pattern);
            if (match) {
                // 提取文件名并返回正确的路径
                const filename = match[1];
                return `/ota/${filename}.html`;
            }
        }
        
        // 处理缺少 ota/ 前缀的情况
        const missingOtaPatterns = [
            // 匹配 /releases.html 或 /index.html（在根目录）
            /^\/(releases|index)\.html$/,
            // 匹配完整URL中缺少 ota/ 的情况
            /https?:\/\/[^\/]+\/(releases|index)\.html/,
            // 匹配 localhost 缺少 ota/ 的情况
            /localhost:\d+\/(releases|index)\.html/,
        ];
        
        // 检查是否匹配缺少 ota/ 前缀的模式
        for (const pattern of missingOtaPatterns) {
            const match = url.match(pattern);
            if (match) {
                // 提取文件名并添加 ota/ 前缀
                const filename = match[1];
                // index.html 应该在根目录，releases.html 需要添加 ota/
                if (filename === 'releases') {
                    return `/ota/${filename}.html`;
                }
                return `/${filename}.html`;
            }
        }
        
        // 处理完整的URL（包括http://和https://）
        if (url.startsWith('http://') || url.startsWith('https://')) {
            const parsedUrl = new URL(url);
            // 如果是外部链接（不是当前域名），直接返回原URL
            if (parsedUrl.hostname !== window.location.hostname) {
                return url;
            }
            // 如果是内部链接，返回pathname
            return parsedUrl.pathname;
        }
        
        // 处理绝对路径
        if (url.startsWith('/')) {
            return url;
        }
        
        // 处理相对路径
        const baseUrl = window.location.origin + window.location.pathname;
        const resolvedUrl = new URL(url, baseUrl);
        
        return resolvedUrl.pathname;
    } catch (error) {
        console.warn('URL规范化失败:', error, url);
        // 返回原始URL作为备选
        return url;
    }
}
```

## 说明
这个版本增加了对缺少`ota/`前缀的处理，能够处理以下情况：
- `http://localhost:8080/releases.html` → `/ota/releases.html`
- `http://localhost:8080/index.html` → `/index.html`
- `https://pyspos.us.ci/releases.html` → `/ota/releases.html`
- `https://pyspos.us.ci/index.html` → `/index.html`

注意：`index.html`应该在根目录，而`releases.html`应该在`ota/`目录下。

---

## normalizeUrl 函数的旧实现（版本7 - 只处理releases.html的ota/前缀）

```javascript
function normalizeUrl(url) {
    try {
        // 使用正则表达式精确处理重复路径问题
        const duplicatePathPatterns = [
            // 匹配 ota/ota/index.html 或 ota/ota/releases.html
            /\/ota\/ota\/(index|releases)\.html/,
            // 匹配多次重复的 ota 路径
            /\/ota(?:\/ota)+\/(index|releases)\.html/,
            // 匹配完整URL中的重复路径
            /https?:\/\/[^\/]+\/ota\/ota\/(index|releases)\.html/,
            // 匹配 localhost 的重复路径
            /localhost:\d+\/ota\/ota\/(index|releases)\.html/,
        ];
        
        // 检查是否匹配重复路径模式
        for (const pattern of duplicatePathPatterns) {
            const match = url.match(pattern);
            if (match) {
                // 提取文件名并返回正确的路径
                const filename = match[1];
                return `/ota/${filename}.html`;
            }
        }
        
        // 处理缺少 ota/ 前缀的情况（只处理releases.html）
        const missingOtaPatterns = [
            // 只匹配 /releases.html（因为releases.html在ota目录下）
            /^\/releases\.html$/,
            // 匹配完整URL中缺少 ota/ 的情况（只处理releases.html）
            /https?:\/\/[^\/]+\/releases\.html$/,
            // 匹配 localhost 缺少 ota/ 的情况（只处理releases.html）
            /localhost:\d+\/releases\.html$/,
        ];
        
        // 检查是否匹配缺少 ota/ 前缀的模式
        for (const pattern of missingOtaPatterns) {
            const match = url.match(pattern);
            if (match) {
                // releases.html 需要添加 ota/ 前缀
                return `/ota/releases.html`;
            }
        }
        
        // 处理完整的URL（包括http://和https://）
        if (url.startsWith('http://') || url.startsWith('https://')) {
            const parsedUrl = new URL(url);
            // 如果是外部链接（不是当前域名），直接返回原URL
            if (parsedUrl.hostname !== window.location.hostname) {
                return url;
            }
            // 如果是内部链接，返回pathname
            return parsedUrl.pathname;
        }
        
        // 处理绝对路径
        if (url.startsWith('/')) {
            return url;
        }
        
        // 处理相对路径
        const baseUrl = window.location.origin + window.location.pathname;
        const resolvedUrl = new URL(url, baseUrl);
        
        return resolvedUrl.pathname;
    } catch (error) {
        console.warn('URL规范化失败:', error, url);
        // 返回原始URL作为备选
        return url;
    }
}
```

## 说明
这个版本修正了之前的逻辑，只处理`releases.html`缺少`ota/`前缀的情况，而不再处理`index.html`。这是因为：
- `index.html`应该在根目录：`/index.html`
- `releases.html`应该在`ota/`目录下：`/ota/releases.html`

这样就不会错误地将`http://localhost:8080/index.html`纠正为`/ota/index.html`了。

---

## normalizeUrl 函数的旧实现（版本8 - 修复完整URL的处理逻辑）

```javascript
function normalizeUrl(url) {
    try {
        // 使用正则表达式精确处理重复路径问题
        const duplicatePathPatterns = [
            // 匹配 ota/ota/index.html 或 ota/ota/releases.html
            /\/ota\/ota\/(index|releases)\.html/,
            // 匹配多次重复的 ota 路径
            /\/ota(?:\/ota)+\/(index|releases)\.html/,
            // 匹配完整URL中的重复路径
            /https?:\/\/[^\/]+\/ota\/ota\/(index|releases)\.html/,
            // 匹配 localhost 的重复路径
            /localhost:\d+\/ota\/ota\/(index|releases)\.html/,
        ];
        
        // 检查是否匹配重复路径模式
        for (const pattern of duplicatePathPatterns) {
            const match = url.match(pattern);
            if (match) {
                // 提取文件名并返回正确的路径
                const filename = match[1];
                return `/ota/${filename}.html`;
            }
        }
        
        // 处理缺少 ota/ 前缀的情况（只处理releases.html）
        const missingOtaPatterns = [
            // 只匹配 /releases.html（因为releases.html在ota目录下）
            /^\/releases\.html$/,
            // 匹配 localhost 缺少 ota/ 的情况（只处理releases.html）
            /localhost:\d+\/releases\.html$/,
        ];
        
        // 检查是否匹配缺少 ota/ 前缀的模式
        for (const pattern of missingOtaPatterns) {
            const match = url.match(pattern);
            if (match) {
                // releases.html 需要添加 ota/ 前缀
                return `/ota/releases.html`;
            }
        }
        
        // 处理完整的URL（包括http://和https://）
        if (url.startsWith('http://') || url.startsWith('https://')) {
            const parsedUrl = new URL(url);
            // 如果是外部链接（不是当前域名），直接返回原URL
            if (parsedUrl.hostname !== window.location.hostname) {
                return url;
            }
            // 如果是内部链接，对pathname进行规范化处理
            const pathname = parsedUrl.pathname;
            
            // 检查pathname是否需要纠正
            // 处理缺少 ota/ 前缀的情况（只处理releases.html）
            const missingOtaPatterns = [
                // 只匹配 /releases.html（因为releases.html在ota目录下）
                /^\/releases\.html$/,
            ];
            
            for (const pattern of missingOtaPatterns) {
                const match = pathname.match(pattern);
                if (match) {
                    // releases.html 需要添加 ota/ 前缀
                    return `/ota/releases.html`;
                }
            }
            
            // 如果不需要纠正，返回pathname
            return pathname;
        }
        
        // 处理绝对路径
        if (url.startsWith('/')) {
            return url;
        }
        
        // 处理相对路径
        const baseUrl = window.location.origin + window.location.pathname;
        const resolvedUrl = new URL(url, baseUrl);
        
        return resolvedUrl.pathname;
    } catch (error) {
        console.warn('URL规范化失败:', error, url);
        // 返回原始URL作为备选
        return url;
    }
}
```

## 说明
这个版本修复了完整URL的处理逻辑。之前的版本在处理完整URL（如`https://pyspos.us.ci/index.html`）时，直接返回pathname，没有对pathname进行规范化处理。这导致`https://pyspos.us.ci/index.html`不会被纠正为`/index.html`。

现在的逻辑：
1. 先检查是否是完整URL（http://或https://开头）
2. 如果是完整URL，提取pathname
3. 检查pathname是否需要纠正（如`/releases.html`需要添加`ota/`前缀）
4. 如果不需要纠正，返回pathname
5. 这样就能正确处理：
   - `https://pyspos.us.ci/index.html` → `/index.html`（正确）
   - `https://pyspos.us.ci/releases.html` → `/ota/releases.html`（正确）
   - `http://localhost:8080/index.html` → `/index.html`（正确）
   - `http://localhost:8080/releases.html` → `/ota/releases.html`（正确）
