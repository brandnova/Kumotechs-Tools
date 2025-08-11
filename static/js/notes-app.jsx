// static/js/notes-app.jsx

const { useState } = React;

function NotesApp() {
    const [notes, setNotes] = useState([
        { id: 1, title: 'Welcome!', content: 'This is your first note. Click edit to modify it.' },
        { id: 2, title: 'Getting Started', content: 'Add new notes using the button below.' }
    ]);
    const [newTitle, setNewTitle] = useState('');
    const [newContent, setNewContent] = useState('');
    const [editingId, setEditingId] = useState(null);

    const addNote = () => {
        if (newTitle.trim() || newContent.trim()) {
            const newNote = {
                id: Date.now(),
                title: newTitle.trim() || 'Untitled',
                content: newContent.trim()
            };
            setNotes([newNote, ...notes]);
            setNewTitle('');
            setNewContent('');
        }
    };

    const deleteNote = (id) => {
        setNotes(notes.filter(note => note.id !== id));
    };

    const startEdit = (note) => {
        setEditingId(note.id);
        setNewTitle(note.title);
        setNewContent(note.content);
    };

    const saveEdit = () => {
        setNotes(notes.map(note => 
            note.id === editingId 
                ? { ...note, title: newTitle || 'Untitled', content: newContent }
                : note
        ));
        setEditingId(null);
        setNewTitle('');
        setNewContent('');
    };

    const cancelEdit = () => {
        setEditingId(null);
        setNewTitle('');
        setNewContent('');
    };

    return (
        <div>
            <div className="mb-6">
                <h2 className="text-xl font-semibold mb-4">
                    {editingId ? 'Edit Note' : 'Add New Note'}
                </h2>
                
                <div className="space-y-3">
                    <input
                        type="text"
                        placeholder="Note title"
                        value={newTitle}
                        onChange={(e) => setNewTitle(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    
                    <textarea
                        placeholder="Write your note here..."
                        value={newContent}
                        onChange={(e) => setNewContent(e.target.value)}
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    
                    <div className="flex gap-2">
                        {editingId ? (
                            <>
                                <button
                                    onClick={saveEdit}
                                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                                >
                                    Save Changes
                                </button>
                                <button
                                    onClick={cancelEdit}
                                    className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                                >
                                    Cancel
                                </button>
                            </>
                        ) : (
                            <button
                                onClick={addNote}
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                            >
                                Add Note
                            </button>
                        )}
                    </div>
                </div>
            </div>

            <div className="border-t pt-6">
                <h2 className="text-xl font-semibold mb-4">Your Notes ({notes.length})</h2>
                
                {notes.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">
                        No notes yet. Add your first note above!
                    </p>
                ) : (
                    <div className="space-y-4">
                        {notes.map(note => (
                            <div key={note.id} className="bg-gray-50 p-4 rounded-lg border">
                                <div className="flex justify-between items-start mb-2">
                                    <h3 className="font-medium text-lg">{note.title}</h3>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => startEdit(note)}
                                            className="text-blue-600 hover:text-blue-800 text-sm"
                                        >
                                            Edit
                                        </button>
                                        <button
                                            onClick={() => deleteNote(note.id)}
                                            className="text-red-600 hover:text-red-800 text-sm"
                                        >
                                            Delete
                                        </button>
                                    </div>
                                </div>
                                {note.content && (
                                    <p className="text-gray-700 whitespace-pre-wrap">{note.content}</p>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

// Mount the app
const root = document.getElementById('notes-app');
if (root) {
    ReactDOM.render(<NotesApp />, root);
}