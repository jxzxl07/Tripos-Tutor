import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"

function Markdown({ children }) {
  return (
    <div className="prose-invert max-w-none leading-relaxed
                    [&_p]:mb-3 [&_ul]:list-disc [&_ul]:ml-5 [&_ul]:mb-3
                    [&_li]:mb-1 [&_strong]:text-white [&_strong]:font-semibold">
      <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
        {children}
      </ReactMarkdown>
    </div>
  )
}

export default Markdown