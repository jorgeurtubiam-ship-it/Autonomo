"""
Browser Tool - Navegación web con Playwright
"""

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from typing import Dict, Any, Optional
from pathlib import Path
import asyncio
import json
from datetime import datetime


class BrowserTool:
    """Tool para navegar por internet usando Playwright"""
    
    name = "browser"
    description = "Navega por internet, visita páginas web, toma screenshots, extrae información, hace click en elementos y más. Útil para web scraping, testing, y automatización web."
    category = "web"
    
    # Instancia compartida del navegador
    _browser: Optional[Browser] = None
    _context: Optional[BrowserContext] = None
    _page: Optional[Page] = None
    _playwright = None
    
    def __init__(self):
        self.screenshots_dir = Path("~/.agent_data/screenshots").expanduser()
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    def get_definition(self) -> Dict[str, Any]:
        """Retorna la definición del tool para el LLM"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["navigate", "screenshot", "extract", "click", "type", "scroll", "wait", "back", "forward", "search", "close"],
                        "description": "Acción a realizar en el navegador"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL a visitar (para action=navigate)"
                    },
                    "selector": {
                        "type": "string",
                        "description": "Selector CSS del elemento (para click, type, wait)"
                    },
                    "text": {
                        "type": "string",
                        "description": "Texto a escribir (para action=type)"
                    },
                    "wait_for": {
                        "type": "string",
                        "description": "Selector a esperar (para action=wait)"
                    },
                    "query": {
                        "type": "string",
                        "description": "Término de búsqueda (para action=search)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout en milisegundos (default: 30000)",
                        "default": 30000
                    }
                },
                "required": ["action"]
            }
        }
    
    async def _ensure_browser(self):
        """Asegura que el navegador esté iniciado"""
        if not self._browser:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            self._context = await self._browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            self._page = await self._context.new_page()
    
    async def _close_browser(self):
        """Cierra el navegador"""
        if self._page:
            await self._page.close()
            self._page = None
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
    
    async def execute(
        self,
        action: str,
        url: Optional[str] = None,
        selector: Optional[str] = None,
        text: Optional[str] = None,
        query: Optional[str] = None,
        wait_for: Optional[str] = None,
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """
        Ejecuta una acción en el navegador
        
        Args:
            action: Acción a realizar (navigate, screenshot, extract, click, type, scroll, wait, back, forward, close)
            url: URL a visitar
            selector: Selector CSS del elemento
            text: Texto a escribir
            wait_for: Selector a esperar
            timeout: Timeout en ms
        
        Returns:
            Dict con success, data, y mensaje
        """
        try:
            # Asegurar que el navegador esté iniciado (excepto para close)
            if action != "close":
                await self._ensure_browser()
            
            # Ejecutar acción
            if action == "navigate":
                return await self._navigate(url, timeout)
            
            elif action == "screenshot":
                return await self._screenshot()
            
            elif action == "extract":
                return await self._extract(selector)
            
            elif action == "click":
                return await self._click(selector, timeout)
            
            elif action == "type":
                return await self._type(selector, text, timeout)
            
            elif action == "scroll":
                return await self._scroll()
            
            elif action == "wait":
                return await self._wait(wait_for or selector, timeout)
            
            elif action == "back":
                return await self._back()
            
            elif action == "forward":
                return await self._forward()
            
            elif action == "search":
                return await self._search(query, timeout)
            
            elif action == "close":
                await self._close_browser()
                return {
                    "success": True,
                    "message": "Navegador cerrado"
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Acción desconocida: {action}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Error en acción {action}: {str(e)}"
            }
    
    async def _navigate(self, url: str, timeout: int) -> Dict[str, Any]:
        """Navega a una URL"""
        if not url:
            return {"success": False, "error": "URL requerida"}
        
        response = await self._page.goto(url, timeout=timeout, wait_until="domcontentloaded")
        
        return {
            "success": True,
            "url": self._page.url,
            "title": await self._page.title(),
            "status": response.status if response else None,
            "message": f"Navegado a {url}"
        }
    
    async def _screenshot(self) -> Dict[str, Any]:
        """Toma un screenshot de la página actual"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        
        await self._page.screenshot(path=str(filepath), full_page=True)
        
        return {
            "success": True,
            "screenshot_path": str(filepath),
            "filename": filename,
            "url": self._page.url,
            "message": f"Screenshot guardado en {filepath}"
        }
    
    async def _extract(self, selector: Optional[str]) -> Dict[str, Any]:
        """Extrae texto de la página o de un elemento"""
        if selector:
            # Extraer texto de un elemento específico
            element = await self._page.query_selector(selector)
            if not element:
                return {"success": False, "error": f"Elemento no encontrado: {selector}"}
            
            text = await element.inner_text()
            return {
                "success": True,
                "text": text,
                "selector": selector,
                "message": f"Texto extraído de {selector}"
            }
        else:
            # Extraer información general de la página
            title = await self._page.title()
            url = self._page.url
            content = await self._page.content()
            
            # Extraer texto visible (limitado a 5000 chars)
            body_text = await self._page.evaluate("() => document.body.innerText")
            body_text = body_text[:5000] if len(body_text) > 5000 else body_text
            
            return {
                "success": True,
                "title": title,
                "url": url,
                "text": body_text,
                "html_length": len(content),
                "message": "Información de página extraída"
            }
    
    async def _click(self, selector: str, timeout: int) -> Dict[str, Any]:
        """Hace click en un elemento"""
        if not selector:
            return {"success": False, "error": "Selector requerido"}
        
        await self._page.click(selector, timeout=timeout)
        
        return {
            "success": True,
            "selector": selector,
            "message": f"Click realizado en {selector}"
        }
    
    async def _type(self, selector: str, text: str, timeout: int) -> Dict[str, Any]:
        """Escribe texto en un elemento"""
        if not selector:
            return {"success": False, "error": "Selector requerido"}
        if not text:
            return {"success": False, "error": "Texto requerido"}
        
        await self._page.fill(selector, text, timeout=timeout)
        
        return {
            "success": True,
            "selector": selector,
            "text": text,
            "message": f"Texto escrito en {selector}"
        }
    
    async def _scroll(self) -> Dict[str, Any]:
        """Hace scroll hacia abajo"""
        await self._page.evaluate("window.scrollBy(0, window.innerHeight)")
        
        return {
            "success": True,
            "message": "Scroll realizado"
        }
    
    async def _wait(self, selector: str, timeout: int) -> Dict[str, Any]:
        """Espera a que un elemento aparezca"""
        if not selector:
            return {"success": False, "error": "Selector requerido"}
        
        await self._page.wait_for_selector(selector, timeout=timeout)
        
        return {
            "success": True,
            "selector": selector,
            "message": f"Elemento {selector} encontrado"
        }
    
    async def _back(self) -> Dict[str, Any]:
        """Navega hacia atrás"""
        await self._page.go_back()
        
        return {
            "success": True,
            "url": self._page.url,
            "message": "Navegado hacia atrás"
        }
    
    async def _forward(self) -> Dict[str, Any]:
        """Navega hacia adelante"""
        await self._page.go_forward()
        
        return {
            "success": True,
            "url": self._page.url,
            "message": "Navegado hacia adelante"
        }

    async def _search(self, query: str, timeout: int) -> Dict[str, Any]:
        """Realiza una búsqueda en Google"""
        if not query:
            return {"success": False, "error": "Query de búsqueda requerida"}
        
        search_url = f"https://www.google.com/search?q={query}"
        await self._page.goto(search_url, timeout=timeout, wait_until="domcontentloaded")
        
        # Extraer resultados principales (texto)
        results = await self._page.evaluate("""() => {
            const items = Array.from(document.querySelectorAll('div.g'));
            return items.slice(0, 5).map(el => {
                const titleEl = el.querySelector('h3');
                const snippetEl = el.querySelector('div.VwiC3b');
                return {
                    title: titleEl ? titleEl.innerText : '',
                    snippet: snippetEl ? snippetEl.innerText : ''
                };
            });
        }""")
        
        return {
            "success": True,
            "query": query,
            "url": self._page.url,
            "results": results,
            "message": f"Búsqueda realizada para: {query}"
        }
