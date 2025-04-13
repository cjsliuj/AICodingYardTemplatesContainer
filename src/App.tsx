import { useEffect } from 'react'
function App() {
    useEffect(() => {
        window.location.replace("/public/index.html")
    }, []);
  return (
    <>
    </>
  )
}
export default App
