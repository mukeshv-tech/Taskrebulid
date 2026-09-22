import codecs
import re

path = 'taskrebuild/extension/src/popup/components/ResourceMonitor.tsx'
code = codecs.open(path, 'r', 'utf-8').read()

code = code.replace(
    '''import { getTaskResourcesStatus, triggerResourceCheck, analyzeResourceReplacement, replaceResourceWithExisting } from '../../lib/api';''',
    '''import { getTaskResourcesStatus, triggerResourceCheck, analyzeResourceReplacement, replaceResourceWithExisting, getTaskActivity } from '../../lib/api';'''
)

code = code.replace(
    '''  const [resources, setResources] = useState<any[]>([]);''',
    '''  const [resources, setResources] = useState<any[]>([]);\n  const [activities, setActivities] = useState<any[]>([]);'''
)

fetch_replacement = '''  const fetchResources = async () => {
    try {
      setLoading(true);
      const data = await getTaskResourcesStatus(taskId);
      setResources(data.resources || []);
      const actData = await getTaskActivity(taskId);
      setActivities(actData || []);'''

code = code.replace(
    '''  const fetchResources = async () => {\n    try {\n      setLoading(true);\n      const data = await getTaskResourcesStatus(taskId);\n      setResources(data.resources || []);''',
    fetch_replacement
)

modal_replacement = '''      {showReplaceModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', width: '90%', maxWidth: '400px' }}>
            <h3 style={{ marginTop: 0 }}>Replace Resource</h3>
            <p style={{ fontSize: '12px' }}>Select an existing resource or activity link to replace the unavailable one.</p>
            
            <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #e5e7eb', padding: '10px', marginBottom: '15px' }}>
              <h5 style={{ margin: '0 0 5px 0' }}>Existing Resources</h5>
              {resources.filter(res => res.id !== showReplaceModal && !res.replaced_by_resource_id).map(res => (
                <div key={res.id} style={{ marginBottom: '5px' }}>
                  <label style={{ fontSize: '12px', display: 'flex', alignItems: 'center' }}>
                    <input 
                      type="radio" 
                      name="replacementCandidate" 
                      value={res.id} 
                      checked={selectedCandidate === res.id}
                      onChange={() => setSelectedCandidate(res.id)}
                      style={{ marginRight: '8px' }}
                    />
                    <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {String(res.title || res.url)}
                    </div>
                  </label>
                </div>
              ))}
              
              <h5 style={{ margin: '15px 0 5px 0' }}>Recent Activity</h5>
              {activities.filter(a => a.url).slice(0, 15).map(act => (
                <div key={act.id} style={{ marginBottom: '5px' }}>
                  <label style={{ fontSize: '12px', display: 'flex', alignItems: 'center' }}>
                    <input 
                      type="radio" 
                      name="replacementCandidate" 
                      value={act.url} 
                      checked={selectedCandidate === act.url}
                      onChange={() => setSelectedCandidate(act.url)}
                      style={{ marginRight: '8px' }}
                    />
                    <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {String(act.title || act.url)}
                    </div>
                  </label>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button onClick={() => setShowReplaceModal(null)} style={{ background: 'white', border: '1px solid #d1d5db', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
              <button onClick={handleConfirmReplace} disabled={!selectedCandidate} style={{ background: '#2563eb', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: selectedCandidate ? 'pointer' : 'not-allowed' }}>Confirm Replacement</button>
            </div>
          </div>
        </div>
      )}'''

code = re.sub(
    r'      \{showReplaceModal && \([\s\S]*?<\/div>\s*<\/div>\s*\)\}',
    modal_replacement,
    code
)

codecs.open(path, 'w', 'utf-8').write(code)
