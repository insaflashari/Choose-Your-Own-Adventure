import {useState, useEffect} from "react"
import {useNavigate} from "react-router-dom";
import axios from "axios";
import ThemeInput from "./ThemeInput.jsx";
import LoadingStatus from "./LoadingStatus.jsx";
import {API_BASE_URL} from "../util.js";


function StoryGenerator() {
    const navigate = useNavigate()
    const [theme, setTheme] = useState("")
    const [jobId, setJobId] = useState(null)
    const [jobStatus, setJobStatus] = useState(null)
    const [error, setError] = useState(null)
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        let pollInterval;

        if (jobId && jobStatus === "processing") {
            pollInterval = setInterval(() => {
                pollJobStatus(jobId)
            }, 5000)
        }

        return () => {
            if (pollInterval) {
                clearInterval(pollInterval)
            }
        }
    }, [jobId, jobStatus]) //if jobid or jobstatus changes, we run this effect

    const generateStory = async (theme) => {
        setLoading(true)
        setError(null) //clear error
        setTheme(theme) //set theme

        try {
            const response = await axios.post(`${API_BASE_URL}/stories/create`, {theme})
            const {job_id, status} = response.data
            setJobId(job_id) //setting jobid and status
            setJobStatus(status)

            pollJobStatus(job_id) //we send request, we get jobid back, and we start polling immediately, until the job is done
        } catch (e) {
            setLoading(false)
            setError(`Failed to generate story: ${e.message}`)
        }
    }

    const pollJobStatus = async (id) => {
        try { 
            const response = await axios.get(`${API_BASE_URL}/jobs/${id}`) 
            const {status, story_id, error: jobError} = response.data
            setJobStatus(status)

            if (status === "completed" && story_id) {
                fetchStory(story_id)
            } else if (status === "failed" || jobError) { //failed or error
                setError(jobError || "Failed to generate story")
                setLoading(false)
            }
        } catch (e) {
            if (e.response?.status !== 404) {
                setError(`Failed to check story status: ${e.message}`) //if we didnt get 404 error, show message
                setLoading(false)
            }
        }
    }

    const fetchStory = async (id) => {
        try {
            setLoading(false)
            setJobStatus("completed")
            navigate(`/story/${id}`) //navigate to this story id page when we try to fetch story
        } catch (e) {
            setError(`Failed to load story: ${e.message}`) //error
            setLoading(false)
        }
    }

    //if there is any error
    const reset = () => {
        setJobId(null)
        setJobStatus(null)
        setError(null)
        setTheme("")
        setLoading(false)
    }

    //error handling
    return <div className="story-generator">
        {error && <div className="error-message"> 
            <p>{error}</p>
            <button onClick={reset}>Try Again</button>
        </div>}

        {!jobId && !error && !loading && <ThemeInput onSubmit={generateStory}/>}

        {loading && <LoadingStatus theme={theme} />}
    </div>
}

export default StoryGenerator