% Minimal offline-compatible shim for elsarticle.cls
% NOTE: this is NOT the official Elsevier elsarticle class. It replicates
% the small subset of macros this paper uses (frontmatter, title, author,
% ead, address, abstract, keyword, journal, linenumbers) on top of the
% standard article class, purely so the .tex source can be compiled in an
% offline sandbox without CTAN access. Before real submission, compile
% with the genuine elsarticle.cls from CTAN / the Elsevier author kit.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{elsarticle}[2026/01/01 offline compatibility shim]
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[11pt,a4paper]{article}

\RequirePackage[margin=1in]{geometry}

\newcommand{\journal}[1]{\gdef\@journal{#1}}
\gdef\@journal{}

\newenvironment{frontmatter}{}{\par\bigskip}

\newcommand{\@ead}{}
\newcommand{\ead}[1]{\gdef\@ead{#1}}

\newcommand{\address}[1]{%
  \begingroup
  \centering
  {\LARGE\bfseries \@title \par}
  \vspace{0.8em}
  {\large \@author \par}
  \vspace{0.4em}
  {\itshape #1 \par}
  \vspace{0.2em}
  \texttt{\@ead}\par
  \endgroup
  \vspace{1.2em}
}

\renewenvironment{abstract}{%
  \par\bigskip\noindent{\bfseries Abstract}\par\smallskip
}{\par\bigskip}

\newenvironment{keyword}{%
  \par\noindent{\bfseries Keywords: }
}{\par}
\newcommand{\sep}{;\ }

