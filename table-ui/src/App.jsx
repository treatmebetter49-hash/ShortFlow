import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import ContentTable from "./components/ContentTable";

export default function App() {
  return (
    <div className="page-bg min-h-screen p-5 flex gap-5">
      <Sidebar />

      <main className="flex-1 min-w-0 flex flex-col gap-5">
        <Header />
        <ContentTable />
      </main>
    </div>
  );
}
