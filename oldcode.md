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
