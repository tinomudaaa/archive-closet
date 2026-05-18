import type { Config, Context } from "https://edge.netlify.com";

export default async function handler(request: Request, context: Context) {
  const url = new URL(request.url);
  const slug = url.searchParams.get("slug");

  // Get the static response from the next step in the request chain
  const response = await context.next();

  // If no slug or if it's not returning HTML, just return the original response
  if (!slug || !response.headers.get("content-type")?.includes("text/html")) {
    return response;
  }

  // Get environment variables securely
  const supabaseUrl = Netlify.env.get("SUPABASE_URL");
  const supabaseKey = Netlify.env.get("SUPABASE_ANON_KEY");

  if (!supabaseUrl || !supabaseKey) {
    return response;
  }

  try {
    // Fetch product from Supabase using the REST API without explicitly selecting 
    // the description column to avoid errors if the column does not exist.
    const res = await fetch(
      `${supabaseUrl}/rest/v1/products?slug=eq.${slug}&limit=1`,
      {
        headers: {
          apikey: supabaseKey,
          Authorization: `Bearer ${supabaseKey}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (!res.ok) {
      return response;
    }

    const products = await res.json();
    if (!products || products.length === 0) {
      return response;
    }

    const product = products[0];
    let html = await response.text();

    const ogTitle = product.name;
    const ogImage = product.image_url;
    // Fallback to "Shop [name] on Archive Closet" if no description exists
    const ogDesc = product.description || `Shop ${product.name} on Archive Closet`;

    // Replace the title tag
    html = html.replace(
      /<title>.*?<\/title>/i,
      `<title>${ogTitle} | Archive Closet</title>`
    );

    // Replace existing description tag
    html = html.replace(
      /<meta\s+name=["']description["'][^>]*>/i,
      ''
    );
    
    // Attempt to clean any hardcoded og: tags if they somehow exist
    html = html.replace(/<meta\s+property=["']og:[^>]+>/gi, '');

    const ogTags = `
        <meta name="description" content="${ogDesc}" />
        <meta property="og:title" content="${ogTitle}" />
        <meta property="og:description" content="${ogDesc}" />
        <meta property="og:image" content="${ogImage}" />
        <meta property="og:type" content="product" />
        <meta property="og:url" content="${request.url}" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="${ogTitle}" />
        <meta name="twitter:description" content="${ogDesc}" />
        <meta name="twitter:image" content="${ogImage}" />
`;

    // Inject before </head>
    html = html.replace(/<\/head>/i, `${ogTags}\n</head>`);

    // Create a new response with the modified HTML
    return new Response(html, {
      status: response.status,
      headers: {
        ...Object.fromEntries(response.headers.entries()),
        "content-type": "text/html; charset=utf-8"
      },
    });
  } catch (error) {
    console.error("Error fetching product for OG tags:", error);
    return response;
  }
}

export const config: Config = {
  path: "/product.html",
};
