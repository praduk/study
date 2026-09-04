I want to create an application to help me study mathematics and remember important things.  This application is a web application with a python-based backend and it supports dark mode, image pasting, and image lightness (not color) inversion to support dark mode.  It must natively support MathJax and it must support document editing with vim keybindings.  The webapp must also be easily usable on a phone (read-only and review).  The primary application is a webapp, with all data located in a subfolder called data relative to the python directory.  The application has no users.  It is password protected and stores sessions.  When launched without any arguments, it launches a webserver and launches a browser that connects to it.  If launched with the --server argument it will just launch the webserver at the located port.  There is a configuration file that defines a password hashkey and port number.  If launched without the --server argument, the password isn't required and it only accepts loopback.

The fundamental language and content is written in MarkDown, however it has native support for MathJax and Excalidraw diagrams with embedded LaTeX.  It also has an editor to easily create commutative diagrams.  It maintains a global list of LaTeX macros that can be used anywhere across the application.

The program orgranizes content into folders.  Each folder has a name and a namespace (for example Mathematics, math).  Namespaces are used to identify content within each folder uniquely without nameclashes.  Because fodlers can be nested, namespaces can be nested.  For example math:algebra.  You can drag/drop move folders and files into other folders which will automatically move their content namespaces.

The entries that a folder can contain are:
Axiom (ax)
Definition (df)
Remark (rk)
Theorem (th)
Problem (pb)

Axioms, Definitions, Theorems, Remarks all have a tag.

Definitions, Theorems, Axioms can have alternative formulations.  One of them is selected as the main formulation, and the others will have their own sub tags.  For example

    math:algebra:df:group

accesses the main definition of a group and

    math:algebra:df:group:category

is say a category-theoretic definition of a group.

Theorems and Problems can have proofs (pf) or solutions (sl).  These in themselves can have have alternatives also tagged.


You can export all content (or certain types of content) in a folder into a PDF file. Content is exported to PDF in the same order as in the folder.  Content can be reordered.

A custom markdown header can be added to content.


Within the markdown editor for all of these you can use $x$ for inline math and $$X$$ for block math.  You can also create and include Excalidraw drawings and images.
Excalidraw has templates that can be used throughout the app.  You can also set the width/size of Excalidraw diagrams.




Now here's the most important part.  This whole thing is supposed to be a highly effective system of studying and remembering things.  Please do detailed research
regarding the science of remembering things and incorporate the best advice into this app.  Spaced repetition of course is a must.  Content is reviewed in the order
they are presented.  You can choose to include/exclude entire folders from review (with a checkbox for each folder, or whatever method you think works best).

Create an AGENTS.md file that describes this project and makes it easy for AI to generate content for your review and also review your existing content for mistakes
and fix them.

The product name is Study.

Study includes in-app Commit and Pull controls for the associated Git repository. The commit action
is limited to authored data, and pull is safe, clean-worktree, fast-forward-only synchronization.

While editing, `@tag` refers to content in staged lexical folder scope. Resolve the current folder,
then its descendant subtree; continue with each parent folder and the sibling subtrees newly visible
at that level. Stop at the first nonempty stage. If that stage has multiple matches, do not guess:
the author must use a fully qualified canonical tag. References support hover/focus/tap previews
using the complete Markdown, MathJax, image, Excalidraw, and commutative-diagram renderer. The Vim
editor has a keyboard-searchable insertion picker for definitions, theorems, and other content.

Insertion controls between siblings can create entries or folders at the selected position. Folders
can also be moved by choosing a parent from the tree. The left library panel can be hidden or resized;
the redundant right panel is omitted. Escape remains a Vim key and never closes the editor; `:q`
closes it explicitly.

Entries and folders can be deleted. Recursive deletion of a non-empty folder must clearly identify
the affected subtree and require deliberate confirmation.

Search and reference resolution must be extremely fast. The full library may be loaded into memory;
use suitable indexes, precomputed scope maps, bounded caches, and immediate invalidation after
writes or pulls.
