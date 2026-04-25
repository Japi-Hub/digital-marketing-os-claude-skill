"""Column alias mappings used by analysis scripts."""

META_ADS_COLUMN_ALIASES = {
    "campaign": ["campaign", "campaign name", "nombre de la campaña", "campaña"],
    "adset": ["ad set", "ad set name", "conjunto de anuncios", "grupo de anuncios", "adset"],
    "ad": ["ad", "ad name", "anuncio", "nombre del anuncio"],
    "spend": ["amount spent", "spend", "importe gastado", "gasto", "inversión", "inversion"],
    "impressions": ["impressions", "impresiones"],
    "reach": ["reach", "alcance"],
    "clicks": ["link clicks", "clicks", "clics en el enlace", "clics", "clics únicos"],
    "leads": ["leads", "resultados", "clientes potenciales", "prospectos", "contacts"],
    "conversions": ["conversions", "compras", "purchases", "ventas", "conversiones"],
    "revenue": ["purchase conversion value", "revenue", "valor de conversión", "ingresos", "ventas valor"],
    "frequency": ["frequency", "frecuencia"],
    "ctr": ["ctr", "ctr link click-through rate", "ctr único", "porcentaje de clics"],
    "cpc": ["cpc", "cost per link click", "costo por clic", "coste por clic"],
    "cpm": ["cpm", "cost per 1,000 impressions", "costo por mil impresiones", "coste por mil impresiones"],
    "cpa": ["cost per result", "costo por resultado", "coste por resultado", "cpa", "cpl"],
}

CONTENT_COLUMN_ALIASES = {
    "date": ["date", "fecha", "published_at", "publication date"],
    "platform": ["platform", "plataforma"],
    "format": ["format", "formato", "content type", "tipo", "tipo de contenido"],
    "topic": ["topic", "tema", "pillar", "pilar", "categoria", "category"],
    "hook": ["hook", "gancho", "headline", "titular", "first line"],
    "reach": ["reach", "alcance"],
    "views": ["views", "reproducciones", "plays", "visualizaciones"],
    "likes": ["likes", "me gusta", "reactions", "reacciones"],
    "comments": ["comments", "comentarios"],
    "shares": ["shares", "compartidos", "envios", "sends"],
    "saves": ["saves", "guardados"],
    "messages": ["messages", "mensajes", "dms", "dm", "whatsapp"],
    "leads": ["leads", "prospectos", "clientes potenciales"],
    "clicks": ["clicks", "clics", "link clicks", "clics en enlace"],
}
