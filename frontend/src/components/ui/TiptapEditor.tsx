import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';

interface TiptapEditorProps {
  content?: string;
  onChange?: (markdown: string) => void;
  placeholder?: string;
  className?: string;
  autofocus?: boolean;
}

export default function TiptapEditor({
  content = '',
  onChange,
  placeholder = '내용을 입력하세요...\n\n# 제목을 쓰려면 # 을 입력하세요',
  className = '',
  autofocus = false,
}: TiptapEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({ placeholder }),
    ],
    content,
    autofocus,
    onUpdate({ editor }) {
      onChange?.(editor.getText() === '' ? '' : editor.getHTML());
    },
  });

  return (
    <div className={`tiptap-wrapper ${className}`}>
      <EditorContent editor={editor} />
    </div>
  );
}
